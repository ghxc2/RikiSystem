"""
    Routes
    ~~~~~~
"""
from flask import Blueprint, jsonify
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from wiki.core import Processor, delete_from_db
from wiki.web.forms import EditorForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.search.Dropdown import *
from wiki.web.user import protect

bp = Blueprint('wiki', __name__)



@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    is_author = page.get_author() == current_user.name
    return render_template('page.html', page=page, author=is_author)

@bp.route('/display_version/<path:url>/<int:page_id>')
@protect
def display_version(page_id, url):
    page = current_wiki.get_or_404(url)
    version = page.get_previous_versions()[page_id-1]
    is_author = page.get_author() == current_user.name
    return render_template('version.html', page=version, author=is_author, version=page_id)

@bp.route('/display_edit/<path:url>/<int:version>')
@protect
def display_edit(url, version):
    page = current_wiki.get_or_404(url)
    edit = page.display_edit(version=version)
    is_author = page.get_author() == current_user.name
    return render_template('edit.html', page=edit, author=is_author, version=version)


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    update = True
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            update = False
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save(update=update)
        if update and (current_user.name != page.get_author()):
            ## Issue is here
            flash("Pending Approval", 'warning')
        else:
            flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page)

@bp.route('/approve_edit/<path:url>/', methods=['GET', 'POST'])
@protect
def approve_edit(url):
    split = url.split('/')
    base_url = split[0]
    version = int(split[1])
    page = current_wiki.get_or_404(base_url)
    page.set_approval(status=True, version=version)
    flash('Page Updated', 'success')
    return redirect(url_for('wiki.display', url=base_url))

@bp.route('/disapprove_edit/<path:url>/', methods=['GET', 'POST'])
@protect
def disapprove_edit(url):
    split = url.split('/')
    base_url = split[0]
    version = int(split[1])
    delete_from_db(url=base_url, version_num=version, version=True)
    page = current_wiki.get_or_404(base_url)
    page.restore_last_version()
    flash('Edit Rejected.', 'success')
    return redirect(url_for('wiki.display', url=base_url))

@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    '''
    This method is used to confirm the deletion of a page with the author, and disallow other users from deleting a page.

    Args:
        url: the url of the page to be deleted

    Returns: Either redirects the user back to the page with an error message, or returns them to the home page.

    '''
    page = current_wiki.get_or_404(url)
    if current_user.name != page.get_author():
        flash('You do not have permission to delete this page.', 'error')
        return redirect(url_for('wiki.display', url=url))

    current_wiki.delete(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/search_autocomplete', methods=['GET', 'POST'])
@protect
def search_autocomplete():
    """
    Method for handling /search_autocomplete requests
    Calls upon autocompleter to return valid json response
    """
    autocomplete = Dropdown(current_wiki.index())
    return autocomplete.render(request.args.get('query', ''))


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/')
def user_index():
    pass


@bp.route('/user/create/')
def user_create():
    pass


@bp.route('/user/<int:user_id>/')
def user_admin(user_id):
    pass


@bp.route('/user/delete/<int:user_id>/')
def user_delete(user_id):
    pass


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
