import datetime
from datetime import timedelta
import requests
# import json

'''
Based in program created by Jesus Bellido <jbellido@utec.edu.pe>
Refactory by Rubén Rivas Medina <rrivas@utec.edu.pe>
'''

class Course:
    id = str()
    code = str()
    name = str()
    section = str()
    professor = str()
    type = str()
    start = str()
    end = str()
    day = int()
    month = int()
    year = int()
    days = []
    zoom_url = str()
    first_week = int()
    last_week = int()


class LinkCreator:
    def __init__(self):
        self.access_token = str()
        self.is_visible_video = True  # Add label for Videoconferencia
        self.is_visible_headers = True  # Add labels for Material de Clase & Actividades
        self.is_visible_links = True  # Create links for Videoconferencia and Grabacion
        self.url_course = '{path}/{course_id}'
        self.url_modules = '{path}/{course_id}/modules?per_page=40'
        self.url_items = '{path}/{course_id}/modules/{module_id}/items'
        self.path = 'https://utec.instructure.com/api/v1/courses'

    def headers(self):
        token = 'Bearer ' + self.access_token
        return {'Authorization': token}

    def get(self, url):
        r = requests.get(url, headers=self.headers())
        if r.status_code >= 400:
            raise Exception("Unauthorized, Verify course and access_token")
        return r.json()

    def post(self, url, data):
        r = requests.post(url, headers=self.headers(), data=data)
        if r.status_code >= 400:
            raise Exception("Unauthorized, Verify course and access_token")
        return r.json()

    def get_modules(self, course_id):
        url = self.url_modules.format(path=self.path, course_id=course_id)
        return self.get(url)

    def get_items(self, course_id, module_id):
        url = self.url_items.format(
            path=self.path,
            course_id=course_id,
            module_id=module_id
        )
        return self.get(url)

    def post_item(self, course_id, module_id, item):
        url = self.url_items.format(
            path=self.path,
            course_id=course_id,
            module_id=module_id
        )
        return self.post(url, item)

    def create_header(self, course_id, module_id, title):
        data = dict()
        data['module_item[title]'] = title
        data['module_item[type]'] = 'SubHeader'
        data['module_item[position]'] = '1'
        data['module_item[indent]'] = '0'
        self.post_item(course_id, module_id, data)

    def configure_week(self, course, module_id, date, week):
        # date_start = date - timedelta(days=date.weekday())
        date_start = date
        date_end = date_start + timedelta(days=6)

        if self.is_visible_headers:
            self.create_header(course.id, module_id, 'Actividades')

        if self.is_visible_links:
            prefixes = [('Grabación - ', 'https://.')]
            for prefix, url in prefixes:
                if len(course.days) > 1:
                    data = dict()
                    data['module_item[title]'] = format_title(
                        course=course,
                        week=week,
                        month=(date_start + timedelta(days=course.days[1])).strftime("%m"),
                        day=(date_start + timedelta(days=course.days[1])).strftime("%d"),
                        prefix=prefix)
                    data['module_item[type]'] = 'ExternalUrl'
                    data['module_item[position]'] = '1'
                    data['module_item[indent]'] = '1'
                    data['module_item[external_url]'] = url
                    data['module_item[new_tab]'] = 1
                    self.post_item(course.id, module_id, data)

                data = dict()
                data['module_item[title]'] = format_title(
                    course=course,
                    week=week,
                    month=(date_start + timedelta(days=course.days[0])).strftime("%m"),
                    day=(date_start + timedelta(days=course.days[0])).strftime("%d"),
                    prefix=prefix)
                data['module_item[type]'] = 'ExternalUrl'
                data['module_item[position]'] = '1'
                data['module_item[indent]'] = '1'
                data['module_item[external_url]'] = url
                data['module_item[new_tab]'] = 1
                self.post_item(course.id, module_id, data)

        if self.is_visible_headers:
            self.create_header(course.id, module_id, 'Videoconferencia - Grabaciones')

        if self.is_visible_links:
            prefixes = [('', course.zoom_url)]
            for prefix, url in prefixes:
                if len(course.days) > 1:
                    data = dict()
                    data['module_item[title]'] = format_title(
                        course=course,
                        week=week,
                        month=(date_start + timedelta(days=course.days[1])).strftime("%m"),
                        day=(date_start + timedelta(days=course.days[1])).strftime("%d"),
                        prefix=prefix)
                    data['module_item[type]'] = 'ExternalUrl'
                    data['module_item[position]'] = '1'
                    data['module_item[indent]'] = '1'
                    data['module_item[external_url]'] = url
                    data['module_item[new_tab]'] = 1
                    self.post_item(course.id, module_id, data)

                data = dict()
                data['module_item[title]'] = format_title(
                    course=course,
                    week=week,
                    month=(date_start + timedelta(days=course.days[0])).strftime("%m"),
                    day=(date_start + timedelta(days=course.days[0])).strftime("%d"),
                    prefix=prefix)
                data['module_item[type]'] = 'ExternalUrl'
                data['module_item[position]'] = '1'
                data['module_item[indent]'] = '1'
                data['module_item[external_url]'] = url
                data['module_item[new_tab]'] = 1
                self.post_item(course.id, module_id, data)

        if self.is_visible_video:
            header = "Videoconferencia - Invitaciones - Semana {sm}/{sd} - {em}/{ed}".format(
                sm=date_start.strftime("%m"),
                sd=date_start.strftime("%d"),
                em=date_end.strftime("%m"),
                ed=date_end.strftime("%d")
            )
            self.create_header(course.id, module_id, header)

        if self.is_visible_headers:
            self.create_header(course.id, module_id, 'Material de clase')

    def run(self):
        with open("courses.txt", "r", encoding='utf-8') as file:
            file.readline()
            self.access_token = file.readline().strip()
            file.readline()
            for line in [x.split('|') for x in file.readlines()]:
                course = Course()
                course.id = line[0]
                course.code = line[1]
                course.name = line[2]
                course.section = line[3]
                course.professor = line[4]
                course.type = line[5]
                course.start = line[6]
                course.end = line[7]
                course.day = int(line[8])
                course.month = int(line[9])
                course.year = int(line[10])
                course.days = [int(x)-1 for x in line[11].split(',')]
                course.zoom_url = line[12]
                course.first_week = int(line[13])
                course.last_week = int(line[14])

                print("Configuring", course.code, "-", course.name)

                first_date = datetime.datetime(
                    year=course.year,
                    month=course.month,
                    day=course.day)
                delta = timedelta(days=7)

                i = 0
                for module in self.get_modules(course.id):
                    if module['name'].startswith('Semana '):
                        i += 1
                        if course.first_week <= i <= course.last_week:
                            print("Configuring", module['name'])
                            self.configure_week(course, module['id'], first_date, i)
                            first_date = first_date + delta
                print('It seams we finished ... please REFRESH your browser to see to new configuration !')


def format_title(course, week, month, day, prefix=''):
    title = '{prefix}2020-1 {code} ES {name}, {section}, Semana{week:02d}, {professor}, ' \
            '{mm}/{dd}, {start} - {end} {type}'.\
        format(
            prefix=prefix,
            code=course.code,
            name=course.name,
            section=course.section,
            week=week,
            professor=course.professor,
            mm=month,
            dd=day,
            start=course.start,
            end=course.end,
            type=course.type
        )
    return title
