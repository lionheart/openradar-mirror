import optparse
import logging
import os
import requests
import pickle
import datetime
import json
import pprint

from redis import StrictRedis as Redis
import httplib

from dateutil import parser as date_parser

from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

GITHUB_API_ENDPOINT = "https://api.github.com"
OPENRADAR_API_ENDPOINT = "http://openradar.me/api/radars"

github_url = lambda *components: "{}/{}".format(GITHUB_API_ENDPOINT, "/".join(components))
HEADERS = {
    'Authorization': "token {}".format(settings.GITHUB_API_KEY),
    'Content-Type': "application/json",
    'Accept': "application/json"
}

label_url = github_url("repos", "lionheart", "openradar-mirror", "labels")
milestone_url = github_url("repos", "lionheart", "openradar-mirror", "milestones")
issues_url = github_url("repos", "lionheart", "openradar-mirror", "issues")

requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)

def should_add_given_labels(label_name, labels):
    if label_name in labels:
        return True
    else:
        label_data = {
            'name': label_name,
            'color': "444444"
        }
        response = requests.post(label_url, data=json.dumps(label_data), headers=HEADERS)
        return response.status_code == 201


class Command(BaseCommand):
    def handle(self, *args, **options):
        r = Redis.from_url(settings.REDIS_URL)

        LAST_MODIFIED_MAX_KEY = "last_modified_max"
        LAST_MODIFIED_MIN_KEY = "last_modified_min"
        RADARS_KEY = "radars"

        last_modified_max_pickle = r.get(LAST_MODIFIED_MAX_KEY)
        if last_modified_max_pickle is None:
            last_modified_max = datetime.datetime.now() - datetime.timedelta(weeks=52*30)
        else:
            last_modified_max = pickle.loads(last_modified_max_pickle)

        last_modified_min_pickle = r.get(LAST_MODIFIED_MIN_KEY)
        if last_modified_min_pickle is None:
            last_modified_min = datetime.datetime.now()
        else:
            last_modified_min = pickle.loads(last_modified_min_pickle)

        rate_limit_response = requests.get(GITHUB_API_ENDPOINT + "/rate_limit", headers=HEADERS)
        rate_limit_response_json = rate_limit_response.json()
        if rate_limit_response_json['rate']['remaining'] == 0:
            reset_timestamp = rate_limit_response_json['rate']['reset']
            reset_dt = datetime.datetime.fromtimestamp(reset_timestamp).isoformat()
            print "Rate limit reached, waiting until", reset_dt, "to restart"
            return

        all_milestones = {}
        milestone_paging_url = milestone_url
        while True:
            milestone_response = requests.get(milestone_paging_url, params={"state": "all"}, headers=HEADERS)
            milestone_pages = []
            milestone_paging_url = None
            for link in milestone_response.headers['link'].split(', '):
                url, rel = link.split("; ")
                if rel == 'rel="next"':
                    milestone_paging_url = url[1:-1]

            for milestone_entry in milestone_response.json():
                all_milestones[milestone_entry['title']] = milestone_entry['number']

            if milestone_paging_url is None:
                break

        all_labels = set()
        labels_paging_url = label_url
        while True:
            labels_response = requests.get(labels_paging_url, headers=HEADERS)
            labels_pages = []
            labels_paging_url = None
            for link in labels_response.headers['link'].split(', '):
                url, rel = link.split("; ")
                if rel == 'rel="next"':
                    labels_paging_url = url[1:-1]

            for labels_entry in labels_response.json():
                all_labels.add(labels_entry['name'])

            if labels_paging_url is None:
                break

        page = 1
        params = {
            'page': page,
        }

        while True:
            openradar_response = requests.get(OPENRADAR_API_ENDPOINT, params=params)
            if openradar_response.status_code == 200:
                openradar_json = openradar_response.json()
                if 'result' in openradar_json and len(openradar_json['result']) > 0:
                    result = openradar_json['result']

                    for entry in result:
                        entry_modified = date_parser.parse(entry['modified'])
                        radar_id = entry['number']

                        entry['modified'] = entry_modified.isoformat()

                        try:
                            entry['originated'] = date_parser.parse(entry['originated']).isoformat()
                        except ValueError:
                            print "Date in invalid format, skipping", entry['originated']

                        if not (last_modified_min <= entry_modified <= last_modified_max):
                            title = u"{number}: {title}".format(**entry)
                            description = u"#### Description\n\n{description}\n\n-\nProduct Version: {product_version}\nCreated: {created}\nOriginated: {originated}\nOpen Radar Link: http://www.openradar.me/{number}".format(**entry)
                            data = {
                                'title': title,
                                'body': description,
                            }

                            product = entry['product']
                            if product in all_milestones:
                                data['milestone'] = int(all_milestones[product])
                            else:
                                milestone_data = {
                                    'title': product
                                }
                                milestone_response = requests.post(milestone_url, data=json.dumps(milestone_data), headers=HEADERS)
                                if milestone_response.status_code == 201:
                                    milestone_id = milestone_response.json()['number']
                                    all_milestones[product] = milestone_id
                                    data['milestone'] = milestone_id

                            labels = set()
                            potential_label_keys = ['classification', 'reproducible', 'status']
                            for key in potential_label_keys:
                                if key in entry and len(entry[key]) > 0:
                                    if "duplicate of" in entry[key] or "dup of" in entry[key] or "dupe of" in entry[key]:
                                        label_value = "duplicate"
                                    else:
                                        label_value = entry[key]

                                    label = u"{}:{}".format(key, label_value.lower())
                                    if should_add_given_labels(label, all_labels):
                                        labels.add(label)
                                        all_labels.add(label)

                            data['labels'] = list(labels)

                            if r.hexists(RADARS_KEY, radar_id):
                                # Update the Radar
                                issue_id = r.hget(RADARS_KEY, radar_id)

                                if 'resolved' in entry and len(entry['resolved']) > 0:
                                    data['state'] = 'closed'
                                    comment_body = "Resolved: {resolved}\nModified: {modified}".format(**entry)
                                else:
                                    comment_body = "Modified: {modified}".format(**entry)

                                issue_url = issues_url + "/" + issue_id
                                comment_url = issues_url + "/" + issue_id + "/comments"
                                requests.patch(issue_url, data=json.dumps(data), headers=HEADERS)

                                comment_data = {
                                    'body': comment_body
                                }
                                requests.post(comment_url, json.dumps(comment_data), headers=HEADERS)
                                print "updated", issue_id
                            else:
                                # Add the Radar
                                if 'milestone' not in data:
                                    print "Break"
                                    break

                                try:
                                    response = requests.post(issues_url, data=json.dumps(data), headers=HEADERS)
                                except httplib.IncompleteRead:
                                    print "Error reading response", radar_id
                                else:
                                    if response.status_code == 201:
                                        print u"Added {}".format(title)
                                        if entry_modified < last_modified_min:
                                            last_modified_min = entry_modified
                                            r.set(LAST_MODIFIED_MIN_KEY, pickle.dumps(last_modified_min))

                                        if entry_modified > last_modified_max:
                                            last_modified_max = entry_modified
                                            r.set(LAST_MODIFIED_MAX_KEY, pickle.dumps(last_modified_max))

                                        r.hset(RADARS_KEY, radar_id, response.json()['number'])

                                        if int(response.headers['x-ratelimit-remaining']) == 0:
                                            print "Rate limit exceeded. Backing off."
                                            break
                                    elif response.status_code == 403:
                                        print "403 returned. Backing off."
                                        break
                                    else:
                                        print "Odd status code", radar_id
                    else:
                        # If the loop completes normally, move to the next page
                        params['page'] += 1
                        print "next page"
                        continue

            # We break if continue wasn't called
            break


