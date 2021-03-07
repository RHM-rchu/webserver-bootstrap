# Python Webserver bootstrap

Bootstrap for Python based webserver. Simple webserver in python with option to enable HTTP Authentication, process simple POST & GET request using [Mako](https://www.makotemplates.org/) tempting engine. This is meant to be light and straight to the point, no-frills.

## Getting Started

1. use python 3
2. run `pip install -r requirments.txt`
3. start with `python3 web-server.py`
4. go to host:8081


### Prerequisites

- python3
- pip3


### Setup

Directory structure

```
.
├── html
│   ├── assets
│   │   └── style.css
│   ├── _home.html
│   └── wrapper.html
└── web-server.py
```
1. `web-server.py` is the heart of the app. Modify according to your tastes.
2. HTML directory should be self explanatory
    a. `wrapper.html` wraps all templates base html. 
    b. templates beginning with `_` as in this case `_home.html` are passed to `wrapper.html` with the `${body}` variable.
    c. The started css provided, you'll need to add and adjust according to your taste. There not much there.




## Basic Info

### web-server.py behavior 
if `WEB_REQURE_AUTH = True` variable is set, then auth is enabled and the user is prompted for a user/pass promp. User/Pass is hard. Hostname and Port is also in this config grouping.

Configs are currently inline code in `web-server.py`, at the top. Change accordingly. 
```
WEB_REQURE_AUTH = True
WEB_USERNAME = "user"
WEB_PASSWORD = "pass"
SERVERPORT = 8081
HOSTNAME = ""
```

### Template flow
1. When a page is called we look for a URI or path match.
```
            if self.path.startswith('/list'):
                html_body = render_html_homepage(
                    query_components=query_components
                    )
            else:
                html_body = render_html_homepage(
                    query_components=query_components
                    )
```

2. A function definition is bound to the condition. In this case `def render_html_homepage`. The sample function `render_html_homepage` just inserts the current date into `body.html` and returns the page as `html_body`. Â

3. Final HTML is rendered to `wrapper.html` using **Mako**. `html_body` is assigned to `body` in wrapper.html
```
            htmlwrapper = Template(filename='html/wrapper.html')
            html = htmlwrapper.render(
                body=html_body,
                )
```

4. in `wrapper.html` there is a simplistic sample of a Mako loop, iterating body six times, on the final rendered page
```
            % for i in range(1, 7):
              <div>${i} - ${body}</div>
            % endfor
```
