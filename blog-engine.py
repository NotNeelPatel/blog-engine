import os
import sys
import markdown
import json
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

def readFile(filename: str) -> str:
    """
    Returns the file's content as a str
    """
    fr = open(filename, 'r')
    the_file = fr.read()
    fr.close()
    return the_file

def get_metadata(markdown_file: str) -> list:
    """
    Returns the title, date, and description of a blog post.
    
    All my blog posts have a header that looks like this:
    <!---
    title:Title of My Blog Post
    date:Mon, 29 Aug 2022 13:00:00 EST
    description:Description of my Blog post
    --->

    This function extracts the metadata from this.
    """
    md_file = str(readFile(markdown_file))
    # Raw_data contains the text shown above, minus the HTML comment code
    raw_data = md_file[6:md_file.find("-->") - 2]
    # Split each line
    lines = raw_data.split('\n')

    metadata = ['title', 'date', 'description']
    # Searches for title:, date:, etc and sets that as start of string
    for i in range(len(lines)):
        n = lines[i]
        metadata[i] = n[n.find(':') + 1:]
    
    return metadata

def compile_content(filename: str, header: str, footer: str):
    """
    Compiles header, footer, and content together into one html file
    """

    # Get the file contents
    header = readFile(header)
    footer = readFile(footer)
    content = readFile("content.html")

    # Write and compile to html file
    f = open(filename, 'w')
    f.write(header)
    f.write(content)
    f.write(footer)
    f.close()
    
    # Remove temp files
    if os.path.exists("content.html"):
        os.remove("content.html")
    if os.path.exists("tempheader.html"):
        os.remove("tempheader.html")

def convert_to_html(full_markdown_file: str) -> int:
    """
    Returns True if the markdown file is converted to an html file
    """
    BLOG_HEADER = os.getenv("BLOG_HEADER")
    BLOG_FOOTER = os.getenv("BLOG_FOOTER")
    BLOG_LOCATION = os.getenv("BLOG_LOCATION")
    MK_LOC_LEN = len(os.getenv("MARKDOWN_LOCATION"))
    markdown_file = full_markdown_file[MK_LOC_LEN:]
    #BLOG_HEADER = "blog_post_header.html"
    #BLOG_FOOTER = "blog_post_footer.html"

    try:
        html_file_name = markdown_file.split(".md")[0] + ".html"

        # Getting metadata for <head>
        # metadata = ['url','title','description']
        metadata = get_metadata(full_markdown_file)
        header = readFile(BLOG_HEADER)
        head = header[:header.find('</head>') - 1]
        head += f'\t\t<meta property="og:url" content="https://notneelpatel.github.io/blog/{html_file_name}"/>'
        head += f'\n\t\t<meta property="og:title" content="{metadata[0]}"/>'
        head += f'\n\t\t<meta property="og:description" content="{metadata[2]}"/>\n   '
        header = head + header[header.find('</head>'):]
        # Write new metadata to header
        f = open('tempheader.html', 'w')
        f.write(header)
        f.close()

        # Convert from markdown to html
        markdown.markdownFromFile(input=full_markdown_file, output="content.html")
        
        # Compile header, content, and footer
        compile_content(BLOG_LOCATION + html_file_name, 'tempheader.html', BLOG_FOOTER)
        return(True)
    except:
        print("epic fail!")
        return(False)

def update_blog_home(full_markdown_file: str):
    """
    Adds new blog entry to the blog list and compiles blog home page
    """
    BLOG_LIST = os.getenv("BLOG_LIST")
    HEADER = os.getenv("BLOG_HOME_HEADER")
    FOOTER = os.getenv("BLOG_HOME_FOOTER")
    BLOG_HOME = os.getenv("BLOG_HOME")
    MK_LOC_LEN = len(os.getenv("MARKDOWN_LOCATION"))
    markdown_file = full_markdown_file[MK_LOC_LEN:]
    #BLOG_LIST = "bloglist.md"
    #HEADER = "blog_home_header.html"
    #FOOTER = "blog_home_footer.html"

    # Parse data
    # metadata = ['url','title','description']
    html_file_name = markdown_file.split(".md")[0] + ".html"
    metadata = get_metadata(full_markdown_file)
    date = markdown_file[:10]
    entry = f"{date} [{metadata[0]}](./blog/{html_file_name})"

    previous_content = readFile(BLOG_LIST)
    previous_content = previous_content[31:]

    # Write to blog list
    f = open(BLOG_LIST, 'w')
    f.write(f"## Blog\n[RSS Feed](./feed.xml)\n\n{entry}\n\n_{metadata[2]}..._\n___{previous_content}")
    f.close()
    
    # Convert blog list to html and compile
    markdown.markdownFromFile(input = BLOG_LIST, output = "content.html")
    compile_content(BLOG_HOME, HEADER, FOOTER)

def update_search(full_markdown_file: str):
    """
    Adds new blog entry  to search index
    """
    SEARCH_INDEX = os.getenv("SEARCH_INDEX")
    MK_LOC_LEN = len(os.getenv("MARKDOWN_LOCATION"))
    markdown_file = full_markdown_file[MK_LOC_LEN:]
    #SEARCH_INDEX = "searchindex.json"

    # Parse data
    with open(SEARCH_INDEX) as json_file:
        parsed_json = json.loads(json_file.read())
    
    html_file_name = markdown_file.split(".md")[0] + ".html"
    metadata = get_metadata(full_markdown_file)
    date = markdown_file[:10]
    url = f"https://notneelpatel.github.io/blog/{html_file_name}"

    # Add data to json file
    parsed_json.append({"title": metadata[0], "date":date, "url":url, "description":metadata[2]})

    # Write to json file
    with open(SEARCH_INDEX, "w") as write_file:
        json.dump(parsed_json, write_file)

def update_rss_feed(full_markdown_file: str):
    """
    Adds new blog entry to the rss feed
    """
    FEED = os.getenv("FEED")
    MK_LOC_LEN = len(os.getenv("MARKDOWN_LOCATION"))
    markdown_file = full_markdown_file[MK_LOC_LEN:]
    #FEED = "feed.xml"
    
    # Get data
    metadata = get_metadata(full_markdown_file)
    html_file_name = markdown_file.split(".md")[0] + ".html"
    url = f"https://notneelpatel.github.io/blog/{html_file_name}"
    tree = ET.parse(FEED)
    root = tree.getroot()
    rss_element = root.find('rss')
    channel_element = root.find('channel')
    new_entry = ET.Element("item")

    entry_data = {
        "title": metadata[0],
        "pubDate": metadata[1],
        "link": url,
        "guid":url,
        "description": metadata[2]
        }
    
    # Loop through entry data, putting it into entry
    for key, value in entry_data.items():
        new_element = ET.Element(key)
        new_element.text = value
        new_entry.append(new_element)

    # Append new entry to the feed
    channel_element.append(new_entry)

    # Write to xml file
    tree.write(FEED)

def update_latest(full_markdown_file):
    """
    Updates the blog/latest.html to the latest blog
    """
    LATEST = os.getenv("LATEST")
    MK_LOC_LEN = len(os.getenv("MARKDOWN_LOCATION"))
    markdown_file = full_markdown_file[MK_LOC_LEN:]
    #LATEST = "latest.html"

    html_file_name = markdown_file.split(".md")[0] + ".html"
    f = open(LATEST, 'w')
    f.write(f'<!DOCTYPE html>\n<meta http-equiv="Refresh" content = "0; url=\'{html_file_name}\'"/>\n</html>')
    f.close()


if __name__ == "__main__":
    load_dotenv()
    if len(sys.argv) > 2:
        command = str(sys.argv[1])
        markdown_file = str(sys.argv[2])
        convert_to_html(markdown_file)
    else: 
        markdown_file = str(sys.argv[1])
        if (convert_to_html(markdown_file)):
            update_blog_home(markdown_file)
            update_search(markdown_file)
            update_rss_feed(markdown_file)
            update_latest(markdown_file)


        