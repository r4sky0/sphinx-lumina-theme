"""Test that typography elements render with expected HTML structure."""


def test_list_items_contain_paragraphs(typography_html):
    """Sphinx/MyST wraps list item content in <p> — our CSS depends on this."""
    article = typography_html.find(class_="lumina-article")
    first_li = article.find("ul").find("li")
    assert first_li.find("p") is not None, "Expected <p> inside <li>"


def test_nested_list_structure(typography_html):
    """Nested lists should be <ul> inside <li>."""
    article = typography_html.find(class_="lumina-article")
    # Find any <ul> that is nested inside a <li>
    all_uls = article.find_all("ul")
    nested_ul = None
    for ul in all_uls:
        if ul.parent.name == "li":
            nested_ul = ul
            break
    assert nested_ul is not None, "Expected nested <ul> inside <li>"


def test_task_list_has_expected_classes(typography_html):
    """Task lists should have contains-task-list and task-list-item classes."""
    article = typography_html.find(class_="lumina-article")
    task_ul = article.find("ul", class_="contains-task-list")
    assert task_ul is not None, "Expected <ul class='contains-task-list'>"
    task_li = task_ul.find("li", class_="task-list-item")
    assert task_li is not None, "Expected <li class='task-list-item'>"
    checkbox = task_li.find("input", class_="task-list-item-checkbox")
    assert checkbox is not None, "Expected checkbox input"


def test_table_has_docutils_class(typography_html):
    """Tables should have the docutils class for our CSS to target."""
    article = typography_html.find(class_="lumina-article")
    table = article.find("table")
    assert table is not None, "Expected a <table>"
    assert "docutils" in table.get("class", []), "Expected 'docutils' class on table"


def test_definition_list_structure(typography_html):
    """Definition lists should use <dl> with <dt> and <dd>."""
    article = typography_html.find(class_="lumina-article")
    dl = article.find("dl", class_=lambda c: c and "field-list" not in c)
    assert dl is not None, "Expected a <dl> (non-field-list)"
    assert dl.find("dt") is not None, "Expected <dt> in definition list"
    assert dl.find("dd") is not None, "Expected <dd> in definition list"


def test_field_list_structure(typography_html):
    """Field lists should use <dl class='field-list'> with colon spans."""
    article = typography_html.find(class_="lumina-article")
    fl = article.find("dl", class_="field-list")
    assert fl is not None, "Expected <dl class='field-list'>"
    dt = fl.find("dt")
    assert dt is not None, "Expected <dt> in field list"
    colon = dt.find("span", class_="colon")
    assert colon is not None, "Expected <span class='colon'> in field list dt"


def test_kbd_elements_exist(typography_html):
    """<kbd> elements should be present."""
    article = typography_html.find(class_="lumina-article")
    kbd = article.find("kbd")
    assert kbd is not None, "Expected <kbd> element"


def test_hr_exists(typography_html):
    """<hr> element should be present."""
    article = typography_html.find(class_="lumina-article")
    hr = article.find("hr")
    assert hr is not None, "Expected <hr> element"
