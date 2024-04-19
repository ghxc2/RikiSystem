"""
    Wiki core
    ~~~~~~~~~
"""
import copy
import sqlite3
from collections import OrderedDict
from io import open
import os
import re

from flask import abort
from flask import url_for
from flask import current_app
from flask_login import current_user
import markdown
from datetime import datetime

import config


def clean_url(url):
    """
        Cleans the url and corrects various errors. Removes multiple
        spaces and all leading and trailing spaces. Changes spaces
        to underscores and makes all characters lowercase. Also
        takes care of Windows style folders use.

        :param str url: the url to clean


        :returns: the cleaned url
        :rtype: str
    """
    url = re.sub('[ ]{2,}', ' ', url).strip()
    url = url.lower().replace(' ', '_')
    url = url.replace('\\\\', '/').replace('\\', '/')
    return url


def wikilink(text, url_formatter=None):
    """
        Processes Wikilink syntax "[[Link]]" within the html body.
        This is intended to be run after content has been processed
        by markdown and is already HTML.

        :param str text: the html to highlight wiki links in.
        :param function url_formatter: which URL formatter to use,
            will by default use the flask url formatter

        Syntax:
            This accepts Wikilink syntax in the form of [[WikiLink]] or
            [[url/location|LinkName]]. Everything is referenced from the
            base location "/", therefore sub-pages need to use the
            [[page/subpage|Subpage]].

        :returns: the processed html
        :rtype: str
    """
    if url_formatter is None:
        url_formatter = url_for
    link_regex = re.compile(
        r"((?<!\<code\>)\[\[([^<].+?) \s*([|] \s* (.+?) \s*)?]])",
        re.X | re.U
    )
    for i in link_regex.findall(text):
        title = [i[-1] if i[-1] else i[1]][0]
        url = clean_url(i[1])
        html_url = "<a href='{0}'>{1}</a>".format(
            url_formatter('wiki.display', url=url),
            title
        )
        text = re.sub(link_regex, html_url, text, count=1)
    return text


class Processor(object):
    """
        The processor handles the processing of file content into
        metadata and markdown and takes care of the rendering.

        It also offers some helper methods that can be used for various
        cases.
    """

    preprocessors = []
    postprocessors = [wikilink]

    def __init__(self, text):
        """
            Initialization of the processor.

            :param str text: the text to process
        """
        self.md = markdown.Markdown(extensions=[
            'codehilite',
            'fenced_code',
            'meta',
            'tables'
        ])
        self.input = text
        self.markdown = None
        self.meta_raw = None

        self.pre = None
        self.html = None
        self.final = None
        self.meta = None

    def process_pre(self):
        """
            Content preprocessor.
        """
        current = self.input
        for processor in self.preprocessors:
            current = processor(current)
        self.pre = current

    def process_markdown(self):
        """
            Convert to HTML.
        """
        self.html = self.md.convert(self.pre)


    def split_raw(self):
        """
            Split text into raw meta and content.
        """
        self.meta_raw, self.markdown = self.pre.split('\n\n', 1)

    def process_meta(self):
        """
            Get metadata.

            .. warning:: Can only be called after :meth:`html` was
                called.
        """
        # the markdown meta plugin does not retain the order of the
        # entries, so we have to loop over the meta values a second
        # time to put them into a dictionary in the correct order
        self.meta = OrderedDict()
        for line in self.meta_raw.split('\n'):
            key = line.split(':', 1)[0]
            # markdown metadata always returns a list of lines, we will
            # reverse that here
            self.meta[key.lower()] = \
                '\n'.join(self.md.Meta[key.lower()])

    def process_post(self):
        """
            Content postprocessor.
        """
        current = self.html
        for processor in self.postprocessors:
            current = processor(current)
        self.final = current

    def process(self):
        """
            Runs the full suite of processing on the given text, all
            pre and post processing, markdown rendering and meta data
            handling.
        """
        self.process_pre()
        self.process_markdown()
        self.split_raw()
        self.process_meta()
        self.process_post()

        return self.final, self.markdown, self.meta


def connect_to_db():
    '''
    This method makes a connection to the sqlite3 database used in our system.

    :returns: a connection and cursor to use for query execution
    '''
    connection = sqlite3.connect(config.DATABASE)
    cursor = connection.cursor()

    return connection, cursor


class Page(object):
    def __init__(self, path, url, new=False):
        self.path = path
        self.url = url
        self._meta = OrderedDict()
        if not new:
            self.load()
            self.render()

    def __repr__(self):
        return "<Page: {}@{}>".format(self.url, self.path)

    def load(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def render(self):
        processor = Processor(self.content)
        self._html, self.body, self._meta = processor.process()

    def save(self, update=True, save_db=True):
        folder = os.path.dirname(self.path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(self.path, 'w', encoding='utf-8') as f:
            for key, value in list(self._meta.items()):
                line = '%s: %s\n' % (key, value)
                f.write(line)
            f.write('\n')
            f.write(self.body.replace('\r\n', '\n'))
        if save_db:
            self.load()
            self.save_to_db(update=update)
        self.render()


    def save_to_db(self, update):
        """
        This method saves a new wiki page edit to the database. It first finds the most recent version given the url,
        and then it inserts the previous version for the most recent update.

        It takes an argument values that specifies the url, version, and content to insert into the database.
        """
        connection, cursor = connect_to_db()
        version = 1
        author = current_user.name
        approved = True

        if update:
            version = self.get_last_version() + 1
            approved = True if author == self.get_author() else False


        insert_query = '''INSERT INTO wiki_pages (url, version, content, date_created, author, approved)
                            VALUES (?, ?, ?, ?, ?, ?)'''


        cursor.execute(insert_query, (self.url, version, self.content, datetime.now(), author, approved))

        connection.commit()
        connection.close()

    def get_version_count(self):
        '''
        This method returns the number of versions attributed to a page.

        :returns: int
        '''
        conn, cursor = connect_to_db()

        query = '''SELECT COUNT(*)
                    FROM wiki_pages
                    WHERE url = ?'''
        cursor.execute(query, (self.url,))
        count = cursor.fetchone()[0]
        conn.close()

        return count

    def get_last_version(self, approved=True):
        '''
        This method returns the most recent version number of the page.

        :returns: int
        '''
        conn, cursor = connect_to_db()
        query = '''SELECT MAX(version) AS max_version
                        FROM wiki_pages
                        WHERE url = ? AND approved = ?'''
        cursor.execute(query, (self.url, approved, ))
        max_version = cursor.fetchone()[0]

        return max_version

    def get_previous_versions(self):
        '''
        This method pulls data from previous versions of a page from the database, and populates a temp page object to
        user for rendering a previous version.

        :returns: array of Page objects
        '''
        conn, cursor = connect_to_db()
        pages = []

        query = '''SELECT content
                    FROM wiki_pages
                    WHERE url = ? AND version = ?'''

        for i in range(self.get_version_count()-1):
            cursor.execute(query, (self.url, i + 1))
            content = cursor.fetchone()[0]
            page = Page(self.path, self.url + f"/{i + 1}")
            page.load_content(content)
            page.render()
            pages.append(page)

        conn.close()

        return pages

    def get_pending_edits(self):
        '''
        This method is used to return the version numbers of edits that have not been reviewed by the page author yet.

        Returns: array of ints
        '''
        conn, cursor = connect_to_db()
        query = '''SELECT version FROM wiki_pages WHERE url=? AND approved=?'''

        cursor.execute(query, (self.url, False, ))
        results = cursor.fetchall()
        conn.close()

        versions = [result[0] for result in results]
        return versions

    def display_edit(self, version):
        '''
        This method loads, renders, and returns a pending edit for an author to review.

        version: int
        returns: Page
        '''
        conn, cursor = connect_to_db()

        query = '''SELECT content FROM wiki_pages WHERE url=? AND version=?'''
        cursor.execute(query, (self.url, version, ))
        content = cursor.fetchone()[0]
        edit = Page(self.path, self.url + f"/{version}")
        edit.load_content(content)
        edit.render()

        conn.close()
        return edit

    def set_approval(self, status, version):
        '''
        This method is used to change the approval status of an edit made to a page.
        Args:
            status: boolean
            version: int

        Returns: void

        '''
        conn, cursor = connect_to_db()
        query = '''UPDATE wiki_pages 
                    SET approved = ?
                     WHERE url = ? and version = ?'''
        cursor.execute(query, (status, self.url, version,))
        conn.commit()
        conn.close()

    def get_approval(self, version):
        '''
        This method gets the approval status of a page version.
        Args:
            version: int

        Returns: boolean

        '''
        conn, cursor = connect_to_db()
        cursor.execute('''SELECT approved FROM wiki_pages WHERE url=? AND version=?''', (self.url, version, ))
        approved = cursor.fetchone()
        conn.close()

        return approved

    def restore_last_version(self):
        '''
        This method updates the page content to the last approved version.
        '''
        conn, cursor = connect_to_db()
        last_version = self.get_last_version()

        content_query = '''SELECT content FROM wiki_pages WHERE url = ? AND version = ?'''
        cursor.execute(content_query, (self.url, last_version, ))
        content = cursor.fetchone()[0]
        self.load_content(content)
        self.render()
        self.save(update=True, save_db=False)


    @property
    def meta(self):
        return self._meta

    def __getitem__(self, name):
        return self._meta[name]

    def __setitem__(self, name, value):
        self._meta[name] = value

    @property
    def html(self):
        return self._html

    def __html__(self):
        return self.html

    @property
    def title(self):
        try:
            return self['title']
        except KeyError:
            return self.url

    @title.setter
    def title(self, value):
        self['title'] = value

    @property
    def tags(self):
        try:
            return self['tags']
        except KeyError:
            return ""

    @tags.setter
    def tags(self, value):
        self['tags'] = value

    def load_content(self, value):
        self.content = value

    def get_author(self):
        '''
        This method is used to fetch the database and get the username of the author of the current page.
        '''

        conn, cursor = connect_to_db()

        query = '''SELECT author FROM wiki_pages WHERE url=? AND version=1'''
        cursor.execute(query, (self.url,))
        author = cursor.fetchone()[0]
        conn.close()


        return author


def delete_from_db(url, version_num=None, version=False):
    """
    This method removes all versions of a given wiki page in the database

    :url: the url of the wiki page to be deleted
    """
    conn, cursor = connect_to_db()

    if version:
        cursor.execute('''DELETE FROM wiki_pages WHERE url=? AND version=?''', (url, version_num,))
    else:
        cursor.execute('''DELETE FROM wiki_pages WHERE url=?''', (url,))

    conn.commit()
    conn.close()


def update_url_db(url, newurl):
    """
    This method updates the url stored in the database for wiki page versions when the page is moved.

    :url: existing url for a wiki page
    :newurl: the url that the page is being moved to
    """
    conn, cursor = connect_to_db()

    query = '''UPDATE wiki_pages
                SET url = ?
                WHERE url = ?'''

    cursor.execute(query, (newurl, url))

    conn.commit()
    conn.close()


class Wiki(object):
    def __init__(self, root):
        self.root = root

    def path(self, url):
        return os.path.join(self.root, url + '.md')

    def exists(self, url):
        path = self.path(url)
        return os.path.exists(path)

    def get(self, url):
        path = self.path(url)
        #path = os.path.join(self.root, url + '.md')
        if self.exists(url):
            return Page(path, url)
        return None

    def get_or_404(self, url):
        page = self.get(url)
        if page:
            return page
        abort(404)

    def get_bare(self, url):
        path = self.path(url)
        if self.exists(url):
            return False
        return Page(path, url, new=True)

    def move(self, url, newurl):
        source = os.path.join(self.root, url) + '.md'
        target = os.path.join(self.root, newurl) + '.md'
        # normalize root path (just in case somebody defined it absolute,
        # having some '../' inside) to correctly compare it to the target
        root = os.path.normpath(self.root)
        # get root path longest common prefix with normalized target path
        common = os.path.commonprefix((root, os.path.normpath(target)))
        # common prefix length must be at least as root length is
        # otherwise there are probably some '..' links in target path leading
        # us outside defined root directory
        if len(common) < len(root):
            raise RuntimeError(
                'Possible write attempt outside content directory: '
                '%s' % newurl)
        # create folder if it does not exists yet
        folder = os.path.dirname(target)
        if not os.path.exists(folder):
            os.makedirs(folder)
        os.rename(source, target)
        # change url references in database
        update_url_db(url, newurl)

    def delete(self, url):
        path = self.path(url)
        if not self.exists(url):
            return False
        os.remove(path)
        delete_from_db(url)
        return True

    def index(self):
        """
            Builds up a list of all the available pages.

            :returns: a list of all the wiki pages
            :rtype: list
        """
        # make sure we always have the absolute path for fixing the
        # walk path
        pages = []
        root = os.path.abspath(self.root)
        for cur_dir, _, files in os.walk(root):
            # get the url of the current directory
            cur_dir_url = cur_dir[len(root)+1:]
            for cur_file in files:
                path = os.path.join(cur_dir, cur_file)
                if cur_file.endswith('.md'):
                    url = clean_url(os.path.join(cur_dir_url, cur_file[:-3]))
                    page = Page(path, url)
                    pages.append(page)
        return sorted(pages, key=lambda x: x.title.lower())

    def index_by(self, key):
        """
            Get an index based on the given key.

            Will use the metadata value of the given key to group
            the existing pages.

            :param str key: the attribute to group the index on.

            :returns: Will return a dictionary where each entry holds
                a list of pages that share the given attribute.
            :rtype: dict
        """
        pages = {}
        for page in self.index():
            value = getattr(page, key)
            pre = pages.get(value, [])
            pages[value] = pre.append(page)
        return pages

    def get_by_title(self, title):
        pages = self.index(attr='title')
        return pages.get(title)

    def get_tags(self):
        pages = self.index()
        tags = {}
        for page in pages:
            pagetags = page.tags.split(',')
            for tag in pagetags:
                tag = tag.strip()
                if tag == '':
                    continue
                elif tags.get(tag):
                    tags[tag].append(page)
                else:
                    tags[tag] = [page]
        return tags

    def index_by_tag(self, tag):
        pages = self.index()
        tagged = []
        for page in pages:
            if tag in page.tags:
                tagged.append(page)
        return sorted(tagged, key=lambda x: x.title.lower())

    def search(self, term, ignore_case=True, attrs=['title', 'tags', 'body']):
        pages = self.index()
        regex = re.compile(term, re.IGNORECASE if ignore_case else 0)
        matched = []
        for page in pages:
            for attr in attrs:
                if regex.search(getattr(page, attr)):
                    matched.append(page)
                    break
        return matched
