#!/usr/bin/env python
__description__ = \
"""
Install the website into the github docs folder (like sphinx-build)
"""
__author__ = "Michael J. Harrms"
__usage__ = "build.py source_dir [target_dir]"

import jinja2
import mistune

import sys, os, re, glob, shutil

def generate_hover(image_file,
                   text=None,
                   link=None,
                   html=None,
                   text_class=None,
                   image_class=None,
                   alt_text=None):
    """
    Generate html that encodes hovering-over image effects.

    image_file: an image file (required)
    text: text to show on hover
    link: link when image is clicked on
    html: html to show when image is clicked on (placed after text)
    text_class: class to assign text
    image_class: class to assign image
    alt_text: alt_text to show if image is missing
    """

    # Make sure file exists
    if not os.path.isfile(image_file):
        err = f"Image file ({image_file}) does not exist.\n"
        raise FileNotFoundError(err)

    # Get text class
    if text_class is None:
        text_class = "hover-text"
    else:
        text_class = f"hover-text {text_class}"

    # Get image class
    if image_class is None:
        image_class = "hover-image"
    else:
        text_class = f"hover-text {image_class}"

    # Get alt-text
    if alt_text is None:
        alt_text = "image"

    # Create hover-holder div
    out = []
    out.append(f"<div class=\"hover-holder\" >")

    # Add link
    if link is not None:
        out.append(f"<a href=\"{link}\">")

    # Create image and overlay classes
    out.append(f"<img src=\"{image_file}\" alt=\"{alt_text}\" class=\"{image_class}\">")
    out.append(f"<div class=\"hover-overlay\">")
    if text is not None:
        out.append(f"<div class=\"{text_class}\">{text}</div>")
    if html is not None:
        out.append(html)
    out.append("</div>")

    # Close link
    if link is not None:
        out.append("</a>")

    # Close div
    out.append("</div>")

    return "".join(out)


def parse_markdown(md_file):
    """
    Create pretty html from a markdown file.
    """

    f = open(md_file)
    md = f.read()
    f.close()

    md_parser = mistune.Markdown()

    html = md_parser(md)

    img_pattern = re.compile("<img ")
    html = img_pattern.sub("<img class=\"img-fluid\"",html)

    html = re.sub("<ul>","<ul class=\"list-group\">",html)
    html = re.sub("<li>","<li class=\"list-group-item\">",html)

    dash_pattern = re.compile("--")
    html = dash_pattern.sub("&mdash;",html)

    h1_pattern = re.compile("<h1>.*?</h1>")
    h1_matches = h1_pattern.findall(html)
    if h1_matches:
        for m in h1_matches:
            inner = m.split(">")[1].split("<")[0]
            inner = inner.lower()
            inner = re.sub(" ","-",inner)

            new_header = f"<h1 id=\"{inner}\">{m[4:]}"

            html = re.sub(m,new_header,html)

    hr_pattern = re.compile("\<hr\>")

    out = []
    out.append("<br/><br/>")
    for section in hr_pattern.split(html):
        out.append("<div class=\"container bg-light rounded mx-auto\">")
        out.append("<div class=\"m-3 p-3\">")
        out.append(section)
        out.append("</div></div><br/>")


    return "".join(out)


def generate_from_markdown(md_file,template_file):
    """
    Use jinja to load content from markdown into a template file.
    """

    session = {}
    session["content"] = parse_markdown(md_file)

    root = ".".join(md_file.split(".")[:-1])
    session_to_html(session,template_file,f"{root}.html")


def session_to_html(session,template_file,output_file):
    """
    Use jinja load generated html into an html file.
    """

    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader,
                                      autoescape=jinja2.select_autoescape("html"))
    template = template_env.get_template(template_file)
    output = template.render(session=session)

    f = open(output_file,"w")
    f.write(output)
    f.close()

def install_into(target_dir):

    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)

    os.mkdir(target_dir)

    html_files = glob.glob("*.html",recursive=True)
    to_whack = re.compile("_template.html")
    html_files = [f for f in html_files if not to_whack.search(f)]

    if os.path.isfile("CNAME"):
        html_files.append("CNAME")
    if os.path.isfile(".nojekyll"):
        html_files.append(".nojekyll")

    dirs = [d for d in os.listdir() if os.path.isdir(d) and d[0] != "."]

    for f in html_files:
        shutil.copy(f,target_dir)

    for d in dirs:
        shutil.copytree(d,os.path.join(target_dir,d))


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    try:
        source_dir = argv[0]
    except IndexError:
        err = f"Incorrect arguments. Usage:\n\n{__usage__}\n\n"
        raise ValueError(err)

    # Figure out if we are installing into target_dir
    try:
        target_dir = argv[1]
        target_dir = os.path.abspath(target_dir)
    except IndexError:
        target_dir = None

    os.chdir(source_dir)

    # Generate markdown files
    for md_file in glob.glob("*.md"):
        generate_from_markdown(md_file,"basic_template.html")

    if target_dir is not None:
        install_into(target_dir)


if __name__ == "__main__":
    main()
