import time
from bs4 import BeautifulSoup
from selenium import webdriver


class Crawler:
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path='./chromedriver')
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1440, 900)

    def login(self, email, password):
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(5)

        username_elem = self.driver.find_element('id', 'username')
        username_elem.send_keys(email)
        password_elem = self.driver.find_element('id', 'password')
        password_elem.send_keys(password)

        self.driver.find_element('xpath', "//button[@type='submit']").click()

    def get_profile(self, url):
        self.driver.get(url)
        time.sleep(3)

        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')
        person_link = soup.find('a', {'class': 'app-aware-link'})
        person_url = person_link.get('href')
        self.driver.get(person_url)
        time.sleep(3)

        profile_url = self.driver.current_url
        return profile_url

    def element_exist(self, by, value, start_form=None):
        if start_form is not None:
            return len(start_form.find_elements(by, value)) > 0
        return len(self.driver.find_elements(by, value)) > 0

    def get_title(self, profile_url):
        self.driver.get(profile_url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')
        main = soup.find('main', {'id': 'main'})
        profile_line = main.find('div', {'class': 'text-body-medium'}).getText().strip()
        return profile_line

    def get_about(self, profile_url):
        self.driver.get(profile_url)
        src = self.driver.page_source
        soup = BeautifulSoup(src, 'lxml')
        main = soup.find('main', {'id': 'main'})
        about_section = main.find('section', id=lambda x: x and 'ABOUT-' in x)
        head_line = about_section.find('div', {'class': 'pv-shared-text-with-see-more'}).find('span', {
            "aria-hidden": "true"}).prettify()
        return head_line

    def get_experiences(self, profile_url):
        experience_url = profile_url + 'details/experience/'
        self.driver.get(experience_url)

        if self.element_exist('xpath', "//button.scaffold-finite-scroll__load-button"):
            self.driver.find_element('xpath', "//button.scaffold-finite-scroll__load-button").click()

        time.sleep(3)

        experience_src = self.driver.page_source
        experience_bs_soup = BeautifulSoup(experience_src, 'lxml')
        main = experience_bs_soup.find('main', {'id': 'main'})
        experience_section = main.find('section')
        experience_item_list = experience_section.findAll('li', {'class': 'artdeco-list__item'})
        experiences_list = []
        for experience_item in experience_item_list:
            content_container = experience_item.find('div',
                                                     {'class': 'display-flex flex-column full-width align-self-center'})
            if content_container.find('a', {'data-field': 'position_company_icon'}):
                company_container = content_container.find('a', {'data-field': 'position_company_icon'})
                company_name = company_container.find('div').find('span', {'aria-hidden': 'true'}).getText().strip()
                positions = content_container\
                    .findAll('div', {'class': 'display-flex flex-column full-width align-self-center'})
                for position in positions:
                    position_title = position.find('a').find('div').find('span',
                                                                         {'aria-hidden': 'true'}).getText().strip()
                    other_infos = position.findAll('span', {'class': 't-14 t-normal t-black--light'})
                    position_duration = other_infos[0].find('span', {'aria-hidden': 'true'}).getText().strip()
                    if len(other_infos) == 2:
                        position_location = other_infos[1].find('span', {'aria-hidden': 'true'}).getText().strip()
                    else:
                        position_location = ''
                    position_description_container = position.find('li', {'class': 'pvs-list__item--with-top-padding'})
                    if position_description_container:
                        position_description = position_description_container.find('span',
                                                                                   {'aria-hidden': 'true'}).prettify()
                    else:
                        position_description = ''
                    experiences_list.append({
                        'company': company_name,
                        'position': position_title,
                        'duration': position_duration,
                        'location': position_location,
                        'description': position_description
                    })
            else:
                experience_info_container = content_container\
                    .find('div', {'class': 'display-flex flex-row justify-space-between'})
                position_title = experience_info_container.find('span', {'class': 't-bold mr1'}).find('span', {
                    'aria-hidden': 'true'}).getText().strip()
                company_name = experience_info_container.find('span', {'class': 't-14 t-normal'}).find('span', {
                    'aria-hidden': 'true'}).getText().strip().split(" · ")[0]
                other_infos = experience_info_container.findAll('span', {'class': 't-14 t-normal t-black--light'})
                position_duration = other_infos[0].find('span', {'aria-hidden': 'true'}).getText().strip()
                if len(other_infos) == 2:
                    position_location = other_infos[1].find('span', {'aria-hidden': 'true'}).getText().strip()
                else:
                    position_location = ''
                position_description_container = content_container.find('li',
                                                                        {'class': 'pvs-list__item--with-top-padding'})
                if position_description_container:
                    position_description = position_description_container.find('span',
                                                                               {'aria-hidden': 'true'}).prettify()
                else:
                    position_description = ''
                experiences_list.append({
                    'company': company_name,
                    'position': position_title,
                    'duration': position_duration,
                    'location': position_location,
                    'description': position_description
                })
        return experiences_list

    def get_educations(self, profile_url):
        education_url = profile_url + 'details/education/'
        self.driver.get(education_url)

        if self.element_exist('xpath', "//button.scaffold-finite-scroll__load-button"):
            self.driver.find_element('xpath', "//button.scaffold-finite-scroll__load-button").click()

        time.sleep(3)

        education_src = self.driver.page_source
        education_bs_soup = BeautifulSoup(education_src, 'lxml')
        main = education_bs_soup.find('main', {'id': 'main'})
        education_section = main.find('section')
        education_item_list = education_section.findAll('li', {'class': 'artdeco-list__item'})
        education_list = []

        for education_item in education_item_list:
            education_data_container = education_item.find('div', {
                'class': 'display-flex flex-column full-width align-self-center'})
            school_name = education_data_container.find('div', {'class': 'display-flex align-items-center'}).find(
                'span', {
                    'aria-hidden': 'true'}).getText().strip()
            degree_container = education_data_container.select('span[class="t-14 t-normal"]')
            if degree_container and len(degree_container) > 0:
                degree = degree_container[0].find('span', {'aria-hidden': 'true'}).getText().strip()
            else:
                degree = ''

            duration_container = education_data_container.select('span[class="t-14 t-normal t-black--light"]')
            if duration_container and len(duration_container) > 0:
                duration = duration_container[0].find('span', {'aria-hidden': 'true'}).getText().strip()
            else:
                duration = ''

            education_list.append({
                'school': school_name,
                'degree': degree,
                'duration': duration
            })
        return education_list

    def get_skills(self, profile_url):
        skill_url = profile_url + 'details/skills/'
        self.driver.get(skill_url)

        if self.element_exist('xpath', "//button.scaffold-finite-scroll__load-button"):
            self.driver.find_element('xpath', "//button.scaffold-finite-scroll__load-button").click()

        time.sleep(3)

        skills_src = self.driver.page_source
        education_bs_soup = BeautifulSoup(skills_src, 'lxml')
        main = education_bs_soup.find('main', {'id': 'main'})
        skills_section = main.find('section')

        skills_item_list = skills_section.findAll('li', {'class': 'artdeco-list__item'})
        skills_list = []

        for skill_item in skills_item_list:
            skill_name_container = skill_item.find('span', {'class': 't-bold mr1 hoverable-link-text'})
            if not skill_name_container:
                skill_name_container = skill_item.find('span', {'class': 't-bold mr1'})
            skill_name = skill_name_container.find('span', {'aria-hidden': 'true'}).getText().strip()
            skill_endorsed_container = skill_item.find('span', {'class': 'pvs-entity__supplementary-info t-14'
                                                                         ' t-black--light t-normal mr1'})
            if skill_endorsed_container:
                skill_endorsed = skill_endorsed_container.find('span', {'aria-hidden': 'true'}).getText().strip().split(
                    '· ')[1]
            else:
                skill_endorsed = 0
            skills_list.append({
                'name': skill_name,
                'endorsed': skill_endorsed
            })
        return skills_list

    def get_posts(self, profile_url, last_post=None):
        posts_url = profile_url + 'recent-activity/shares/'
        self.driver.get(posts_url)

        time.sleep(3)

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height <= last_height:
                break

            if last_post is not None:
                data_urn = 'urn:li:activity:' + last_post
                if self.element_exist('xpath', "//div[@data-urn='" + data_urn + "']"):
                    break

            posts = self.driver.find_elements('xpath', '//div[contains(@data-urn, "urn:li:activity:")]')
            if len(posts) >= 100:
                break

            last_height = new_height

        posts_data = []
        posts = self.driver.find_elements('xpath', '//div[contains(@data-urn, "urn:li:activity:")]')
        for post in posts:
            post_id_attr = post.get_attribute('data-urn')
            post_id = post_id_attr.split(':')[-1]

            if last_post and post_id == last_post:
                break

            content = ""
            if self.element_exist('xpath', './/div[contains(@class, "feed-shared-update-v2__description-wrapper")]', post):
                description_wrapper = post\
                    .find_element('xpath', './/div[contains(@class, "feed-shared-update-v2__description-wrapper")]')

                if description_wrapper:
                    content_wrapper = description_wrapper\
                        .find_element('xpath', './/div[contains(@class, "feed-shared-update-v2__commentary")]')
                    direction = content_wrapper.get_attribute('dir')
                    content = content_wrapper.find_element('xpath', './/span[@dir="' + direction + '"]').get_attribute(
                        'innerHTML')
            posts_data.append({
                "post_id": post_id,
                "content": content
            })

        return posts_data
