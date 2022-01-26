from bs4 import BeautifulSoup as bs


# create a file handler to convert all the tags to jinja formatting
class FileConverter:
    def __init__(self, filename):
        self.filename = filename

    # make a route to change particular attributes of a tag
    def change_attributes(self, tag_name, attribute_name):
        # load the file
        soup = self.load_file()

        # get all of one tag --> change it
        tags = soup.find_all(tag_name)

        for tag in tags:
            attribute = tag[attribute_name]

            # check if the attribute should be changed
            if self.check_changability(attribute):
                tag[attribute_name] = self.jinj(attribute)

        # rewrite the file
        self.save_file(soup)

    # make a route to jinjafy
    def jinj(self, attribute, jinja_folder='static'):
        # check if the first character is a backslash
        if attribute[0] == '/':
            attribute = attribute[1:]

        # format using the static folder
        jinja_string = "{{" + \
            f"url_for('{jinja_folder}', filename='{attribute}')" + "}}"

        return jinja_string

    def check_changability(self, attribute):
        changeable = True
        check_section = attribute[:8].lower()

        if 'https' in check_section:
            changeable = False
        elif '{{' in check_section:
            changeable = False

        return changeable

    # make a way to load files to a soup obj
    def save_file(self, soup):
        with open(self.filename, 'w') as outfile:
            outfile.write(soup.prettify())

    # make a way to load files to a soup obj
    def load_file(self):
        with open(self.filename, 'r') as infile:
            soup = bs(infile.read(), 'html.parser')

        return soup
