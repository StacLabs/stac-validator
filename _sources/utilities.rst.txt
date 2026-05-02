Utilities API Reference
=======================

.. raw:: html

    <embed>
    <!doctype html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1" />
    <meta name="generator" content="pdoc 0.9.2" />
    <title>stac_validator.utilities API documentation</title>
    <meta name="description" content="" />
    <link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
    <link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
    <link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
    <style>:root{--highlight-color:#fe9}.flex{display:flex !important}body{line-height:1.5em}#content{padding:20px}#sidebar{padding:30px;overflow:hidden}#sidebar > *:last-child{margin-bottom:2cm}.http-server-breadcrumbs{font-size:130%;margin:0 0 15px 0}#footer{font-size:.75em;padding:5px 30px;border-top:1px solid #ddd;text-align:right}#footer p{margin:0 0 0 1em;display:inline-block}#footer p:last-child{margin-right:30px}h1,h2,h3,h4,h5{font-weight:300}h1{font-size:2.5em;line-height:1.1em}h2{font-size:1.75em;margin:1em 0 .50em 0}h3{font-size:1.4em;margin:25px 0 10px 0}h4{margin:0;font-size:105%}h1:target,h2:target,h3:target,h4:target,h5:target,h6:target{background:var(--highlight-color);padding:.2em 0}a{color:#058;text-decoration:none;transition:color .3s ease-in-out}a:hover{color:#e82}.title code{font-weight:bold}h2[id^="header-"]{margin-top:2em}.ident{color:#900}pre code{background:#f8f8f8;font-size:.8em;line-height:1.4em}code{background:#f2f2f1;padding:1px 4px;overflow-wrap:break-word}h1 code{background:transparent}pre{background:#f8f8f8;border:0;border-top:1px solid #ccc;border-bottom:1px solid #ccc;margin:1em 0;padding:1ex}#http-server-module-list{display:flex;flex-flow:column}#http-server-module-list div{display:flex}#http-server-module-list dt{min-width:10%}#http-server-module-list p{margin-top:0}.toc ul,#index{list-style-type:none;margin:0;padding:0}#index code{background:transparent}#index h3{border-bottom:1px solid #ddd}#index ul{padding:0}#index h4{margin-top:.6em;font-weight:bold}@media (min-width:200ex){#index .two-column{column-count:2}}@media (min-width:300ex){#index .two-column{column-count:3}}dl{margin-bottom:2em}dl dl:last-child{margin-bottom:4em}dd{margin:0 0 1em 3em}#header-classes + dl > dd{margin-bottom:3em}dd dd{margin-left:2em}dd p{margin:10px 0}.name{background:#eee;font-weight:bold;font-size:.85em;padding:5px 10px;display:inline-block;min-width:40%}.name:hover{background:#e0e0e0}dt:target .name{background:var(--highlight-color)}.name > span:first-child{white-space:nowrap}.name.class > span:nth-child(2){margin-left:.4em}.inherited{color:#999;border-left:5px solid #eee;padding-left:1em}.inheritance em{font-style:normal;font-weight:bold}.desc h2{font-weight:400;font-size:1.25em}.desc h3{font-size:1em}.desc dt code{background:inherit}.source summary,.git-link-div{color:#666;text-align:right;font-weight:400;font-size:.8em;text-transform:uppercase}.source summary > *{white-space:nowrap;cursor:pointer}.git-link{color:inherit;margin-left:1em}.source pre{max-height:500px;overflow:auto;margin:0}.source pre code{font-size:12px;overflow:visible}.hlist{list-style:none}.hlist li{display:inline}.hlist li:after{content:',\2002'}.hlist li:last-child:after{content:none}.hlist .hlist{display:inline;padding-left:1em}img{max-width:100%}td{padding:0 .5em}.admonition{padding:.1em .5em;margin-bottom:1em}.admonition-title{font-weight:bold}.admonition.note,.admonition.info,.admonition.important{background:#aef}.admonition.todo,.admonition.versionadded,.admonition.tip,.admonition.hint{background:#dfd}.admonition.warning,.admonition.versionchanged,.admonition.deprecated{background:#fd4}.admonition.error,.admonition.danger,.admonition.caution{background:lightpink}</style>
    <style media="screen and (min-width: 7000px)">@media screen and (min-width:7000px){#sidebar{width:30%;height:100vh;overflow:auto;position:sticky;top:0}#content{width:70%;max-width:100ch;padding:3em 4em;border-left:1px solid #ddd}pre code{font-size:1em}.item .name{font-size:1em}main{display:flex;flex-direction:row-reverse;justify-content:flex-end}.toc ul ul,#index ul{padding-left:1.5em}.toc > ul > li{margin-top:.5em}}</style>
    <style media="print">@media print{#sidebar h1{page-break-before:always}.source{display:none}}@media print{*{background:transparent !important;color:#000 !important;box-shadow:none !important;text-shadow:none !important}a[href]:after{content:" (" attr(href) ")";font-size:90%}a[href][title]:after{content:none}abbr[title]:after{content:" (" attr(title) ")"}.ir a:after,a[href^="javascript:"]:after,a[href^="#"]:after{content:""}pre,blockquote{border:1px solid #999;page-break-inside:avoid}thead{display:table-header-group}tr,img{page-break-inside:avoid}img{max-width:100% !important}@page{margin:0.5cm}p,h2,h3{orphans:3;widows:3}h1,h2,h3,h4,h5,h6{page-break-after:avoid}}</style>
    <script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
    <script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>
    </head>
    <body>
    <main>
    <article id="content">
    <header>
    <h1 class="title">Module <code>stac_validator.utilities</code></h1>
    </header>
    <section id="section-intro">
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">import functools
    import json
    import ssl
    from urllib.parse import urlparse
    from urllib.request import urlopen

    import requests  # type: ignore

    NEW_VERSIONS = [
        &#34;1.0.0-beta.2&#34;,
        &#34;1.0.0-rc.1&#34;,
        &#34;1.0.0-rc.2&#34;,
        &#34;1.0.0-rc.3&#34;,
        &#34;1.0.0-rc.4&#34;,
        &#34;1.0.0&#34;,
    ]


    def is_url(url: str) -&gt; bool:
        &#34;&#34;&#34;Checks whether the input string is a valid URL.

        Args:
            url (str): The string to check.

        Returns:
            bool: True if the input string is a valid URL, False otherwise.
        &#34;&#34;&#34;
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


    def is_valid_url(url: str) -&gt; bool:
        &#34;&#34;&#34;Checks if a given string is a valid URL.

        Args:
            url: A string to check for validity as a URL.

        Returns:
            A boolean value indicating whether the input string is a valid URL.
        &#34;&#34;&#34;
        return urlparse(url).scheme in [&#34;http&#34;, &#34;https&#34;]


    def get_stac_type(stac_content: dict) -&gt; str:
        &#34;&#34;&#34;Determine the type of a STAC resource.

        Given a dictionary representing a STAC resource, this function determines the
        resource&#39;s type and returns a string representing that type. The resource type
        can be one of &#39;Item&#39;, &#39;Catalog&#39;, or &#39;Collection&#39;.

        Args:
            stac_content: A dictionary representing a STAC resource.

        Returns:
            A string representing the type of the STAC resource.

        Raises:
            TypeError: If the input is not a dictionary.
        &#34;&#34;&#34;
        try:
            content_types = [&#34;Item&#34;, &#34;Catalog&#34;, &#34;Collection&#34;]
            if &#34;type&#34; in stac_content and stac_content[&#34;type&#34;] == &#34;Feature&#34;:
                return &#34;Item&#34;
            elif &#34;type&#34; in stac_content and stac_content[&#34;type&#34;] in content_types:
                return stac_content[&#34;type&#34;]
            elif &#34;extent&#34; in stac_content or &#34;license&#34; in stac_content:
                return &#34;Collection&#34;
            else:
                return &#34;Catalog&#34;
        except TypeError as e:
            return str(e)


    def fetch_and_parse_file(input_path: str) -&gt; dict:
        &#34;&#34;&#34;Fetches and parses a JSON file from a URL or local file.

        Given a URL or local file path to a JSON file, this function fetches the file,
        and parses its contents into a dictionary. If the input path is a valid URL, the
        function uses the requests library to download the file, otherwise it opens the
        local file with the json library.

        Args:
            input_path: A string representing the URL or local file path to the JSON file.

        Returns:
            A dictionary containing the parsed contents of the JSON file.

        Raises:
            ValueError: If the input is not a valid URL or local file path.
            requests.exceptions.RequestException: If there is an error while downloading the file.
        &#34;&#34;&#34;
        try:
            if is_url(input_path):
                resp = requests.get(input_path)
                resp.raise_for_status()
                data = resp.json()
            else:
                with open(input_path) as f:
                    data = json.load(f)

            return data
        except (ValueError, requests.exceptions.RequestException) as e:
            raise e


    @functools.lru_cache(maxsize=48)
    def fetch_and_parse_schema(input_path: str) -&gt; dict:
        &#34;&#34;&#34;Fetches and parses a JSON schema file from a URL or local file using a cache.

        Given a URL or local file path to a JSON schema file, this function fetches the file
        and parses its contents into a dictionary. If the input path is a valid URL, the
        function uses the requests library to download the file, otherwise it opens the
        local file with the json library. Additionally, this function caches the results of
        previous function calls to reduce the number of times the file is fetched and parsed.

        Args:
            input_path: A string representing the URL or local file path to the JSON schema file.

        Returns:
            A dictionary containing the parsed contents of the JSON schema file.

        Raises:
            ValueError: If the input is not a valid URL or local file path.
            requests.exceptions.RequestException: If there is an error while downloading the file.
        &#34;&#34;&#34;
        return fetch_and_parse_file(input_path)


    def set_schema_addr(version: str, stac_type: str) -&gt; str:
        &#34;&#34;&#34;Set the URL address for the JSON schema to be used for validating the STAC object.
        Validate new versions at schemas.stacspec.org

        Args:
            version (str): The version number of the STAC object.
            stac_type (str): The type of the STAC object (e.g. &#34;item&#34;, &#34;collection&#34;).

        Returns:
            str: The URL address for the JSON schema.
        &#34;&#34;&#34;
        if version in NEW_VERSIONS:
            return f&#34;https://schemas.stacspec.org/v{version}/{stac_type}-spec/json-schema/{stac_type}.json&#34;
        else:
            return f&#34;https://cdn.staclint.com/v{version}/{stac_type}.json&#34;


    def link_request(
        link: dict,
        initial_message: dict,
    ) -&gt; None:
        &#34;&#34;&#34;Makes a request to a URL and appends it to the relevant field of the initial message.

        Args:
            link: A dictionary containing a &#34;href&#34; key which is a string representing a URL.
            initial_message: A dictionary containing lists for &#34;request_valid&#34;, &#34;request_invalid&#34;,
            &#34;format_valid&#34;, and &#34;format_invalid&#34; URLs.

        Returns:
            None

        &#34;&#34;&#34;
        if is_url(link[&#34;href&#34;]):
            try:
                if &#34;s3&#34; in link[&#34;href&#34;]:
                    context = ssl._create_unverified_context()
                    response = urlopen(link[&#34;href&#34;], context=context)
                else:
                    response = urlopen(link[&#34;href&#34;])
                status_code = response.getcode()
                if status_code == 200:
                    initial_message[&#34;request_valid&#34;].append(link[&#34;href&#34;])
            except Exception:
                initial_message[&#34;request_invalid&#34;].append(link[&#34;href&#34;])
            initial_message[&#34;format_valid&#34;].append(link[&#34;href&#34;])
        else:
            initial_message[&#34;request_invalid&#34;].append(link[&#34;href&#34;])
            initial_message[&#34;format_invalid&#34;].append(link[&#34;href&#34;])</code></pre>
    </details>
    </section>
    <section>
    </section>
    <section>
    </section>
    <section>
    <h2 class="section-title" id="header-functions">Functions</h2>
    <dl>
    <dt id="stac_validator.utilities.fetch_and_parse_file"><code class="name flex">
    <span>def <span class="ident">fetch_and_parse_file</span></span>(<span>input_path: str) ‑> dict</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Fetches and parses a JSON file from a URL or local file.</p>
    <p>Given a URL or local file path to a JSON file, this function fetches the file,
    and parses its contents into a dictionary. If the input path is a valid URL, the
    function uses the requests library to download the file, otherwise it opens the
    local file with the json library.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>input_path</code></strong></dt>
    <dd>A string representing the URL or local file path to the JSON file.</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>A dictionary containing the parsed contents of the JSON file.</p>
    <h2 id="raises">Raises</h2>
    <dl>
    <dt><code>ValueError</code></dt>
    <dd>If the input is not a valid URL or local file path.</dd>
    <dt><code>requests.exceptions.RequestException</code></dt>
    <dd>If there is an error while downloading the file.</dd>
    </dl></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def fetch_and_parse_file(input_path: str) -&gt; dict:
        &#34;&#34;&#34;Fetches and parses a JSON file from a URL or local file.

        Given a URL or local file path to a JSON file, this function fetches the file,
        and parses its contents into a dictionary. If the input path is a valid URL, the
        function uses the requests library to download the file, otherwise it opens the
        local file with the json library.

        Args:
            input_path: A string representing the URL or local file path to the JSON file.

        Returns:
            A dictionary containing the parsed contents of the JSON file.

        Raises:
            ValueError: If the input is not a valid URL or local file path.
            requests.exceptions.RequestException: If there is an error while downloading the file.
        &#34;&#34;&#34;
        try:
            if is_url(input_path):
                resp = requests.get(input_path)
                resp.raise_for_status()
                data = resp.json()
            else:
                with open(input_path) as f:
                    data = json.load(f)

            return data
        except (ValueError, requests.exceptions.RequestException) as e:
            raise e</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.utilities.fetch_and_parse_schema"><code class="name flex">
    <span>def <span class="ident">fetch_and_parse_schema</span></span>(<span>input_path: str) ‑> dict</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Fetches and parses a JSON schema file from a URL or local file using a cache.</p>
    <p>Given a URL or local file path to a JSON schema file, this function fetches the file
    and parses its contents into a dictionary. If the input path is a valid URL, the
    function uses the requests library to download the file, otherwise it opens the
    local file with the json library. Additionally, this function caches the results of
    previous function calls to reduce the number of times the file is fetched and parsed.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>input_path</code></strong></dt>
    <dd>A string representing the URL or local file path to the JSON schema file.</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>A dictionary containing the parsed contents of the JSON schema file.</p>
    <h2 id="raises">Raises</h2>
    <dl>
    <dt><code>ValueError</code></dt>
    <dd>If the input is not a valid URL or local file path.</dd>
    <dt><code>requests.exceptions.RequestException</code></dt>
    <dd>If there is an error while downloading the file.</dd>
    </dl></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">@functools.lru_cache(maxsize=48)
    def fetch_and_parse_schema(input_path: str) -&gt; dict:
        &#34;&#34;&#34;Fetches and parses a JSON schema file from a URL or local file using a cache.

        Given a URL or local file path to a JSON schema file, this function fetches the file
        and parses its contents into a dictionary. If the input path is a valid URL, the
        function uses the requests library to download the file, otherwise it opens the
        local file with the json library. Additionally, this function caches the results of
        previous function calls to reduce the number of times the file is fetched and parsed.

        Args:
            input_path: A string representing the URL or local file path to the JSON schema file.

        Returns:
            A dictionary containing the parsed contents of the JSON schema file.

        Raises:
            ValueError: If the input is not a valid URL or local file path.
            requests.exceptions.RequestException: If there is an error while downloading the file.
        &#34;&#34;&#34;
        return fetch_and_parse_file(input_path)</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.utilities.get_stac_type"><code class="name flex">
    <span>def <span class="ident">get_stac_type</span></span>(<span>stac_content: dict) ‑> str</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Determine the type of a STAC resource.</p>
    <p>Given a dictionary representing a STAC resource, this function determines the
    resource's type and returns a string representing that type. The resource type
    can be one of 'Item', 'Catalog', or 'Collection'.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>stac_content</code></strong></dt>
    <dd>A dictionary representing a STAC resource.</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>A string representing the type of the STAC resource.</p>
    <h2 id="raises">Raises</h2>
    <dl>
    <dt><code>TypeError</code></dt>
    <dd>If the input is not a dictionary.</dd>
    </dl></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def get_stac_type(stac_content: dict) -&gt; str:
        &#34;&#34;&#34;Determine the type of a STAC resource.

        Given a dictionary representing a STAC resource, this function determines the
        resource&#39;s type and returns a string representing that type. The resource type
        can be one of &#39;Item&#39;, &#39;Catalog&#39;, or &#39;Collection&#39;.

        Args:
            stac_content: A dictionary representing a STAC resource.

        Returns:
            A string representing the type of the STAC resource.

        Raises:
            TypeError: If the input is not a dictionary.
        &#34;&#34;&#34;
        try:
            content_types = [&#34;Item&#34;, &#34;Catalog&#34;, &#34;Collection&#34;]
            if &#34;type&#34; in stac_content and stac_content[&#34;type&#34;] == &#34;Feature&#34;:
                return &#34;Item&#34;
            elif &#34;type&#34; in stac_content and stac_content[&#34;type&#34;] in content_types:
                return stac_content[&#34;type&#34;]
            elif &#34;extent&#34; in stac_content or &#34;license&#34; in stac_content:
                return &#34;Collection&#34;
            else:
                return &#34;Catalog&#34;
        except TypeError as e:
            return str(e)</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.utilities.is_url"><code class="name flex">
    <span>def <span class="ident">is_url</span></span>(<span>url: str) ‑> bool</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Checks whether the input string is a valid URL.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>url</code></strong> :&ensp;<code>str</code></dt>
    <dd>The string to check.</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <dl>
    <dt><code>bool</code></dt>
    <dd>True if the input string is a valid URL, False otherwise.</dd>
    </dl></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def is_url(url: str) -&gt; bool:
        &#34;&#34;&#34;Checks whether the input string is a valid URL.

        Args:
            url (str): The string to check.

        Returns:
            bool: True if the input string is a valid URL, False otherwise.
        &#34;&#34;&#34;
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.utilities.is_valid_url"><code class="name flex">
    <span>def <span class="ident">is_valid_url</span></span>(<span>url: str) ‑> bool</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Checks if a given string is a valid URL.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>url</code></strong></dt>
    <dd>A string to check for validity as a URL.</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>A boolean value indicating whether the input string is a valid URL.</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def is_valid_url(url: str) -&gt; bool:
        &#34;&#34;&#34;Checks if a given string is a valid URL.

        Args:
            url: A string to check for validity as a URL.

        Returns:
            A boolean value indicating whether the input string is a valid URL.
        &#34;&#34;&#34;
        return urlparse(url).scheme in [&#34;http&#34;, &#34;https&#34;]</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.utilities.link_request"><code class="name flex">
    <span>def <span class="ident">link_request</span></span>(<span>link: dict, initial_message: dict) ‑> NoneType</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Makes a request to a URL and appends it to the relevant field of the initial message.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>link</code></strong></dt>
    <dd>A dictionary containing a "href" key which is a string representing a URL.</dd>
    <dt><strong><code>initial_message</code></strong></dt>
    <dd>A dictionary containing lists for "request_valid", "request_invalid",</dd>
    </dl>
    <p>"format_valid", and "format_invalid" URLs.</p>
    <h2 id="returns">Returns</h2>
    <p>None</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def link_request(
        link: dict,
        initial_message: dict,
    ) -&gt; None:
        &#34;&#34;&#34;Makes a request to a URL and appends it to the relevant field of the initial message.

        Args:
            link: A dictionary containing a &#34;href&#34; key which is a string representing a URL.
            initial_message: A dictionary containing lists for &#34;request_valid&#34;, &#34;request_invalid&#34;,
            &#34;format_valid&#34;, and &#34;format_invalid&#34; URLs.

        Returns:
            None

        &#34;&#34;&#34;
        if is_url(link[&#34;href&#34;]):
            try:
                if &#34;s3&#34; in link[&#34;href&#34;]:
                    context = ssl._create_unverified_context()
                    response = urlopen(link[&#34;href&#34;], context=context)
                else:
                    response = urlopen(link[&#34;href&#34;])
                status_code = response.getcode()
                if status_code == 200:
                    initial_message[&#34;request_valid&#34;].append(link[&#34;href&#34;])
            except Exception:
                initial_message[&#34;request_invalid&#34;].append(link[&#34;href&#34;])
            initial_message[&#34;format_valid&#34;].append(link[&#34;href&#34;])
        else:
            initial_message[&#34;request_invalid&#34;].append(link[&#34;href&#34;])
            initial_message[&#34;format_invalid&#34;].append(link[&#34;href&#34;])</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.utilities.set_schema_addr"><code class="name flex">
    <span>def <span class="ident">set_schema_addr</span></span>(<span>version: str, stac_type: str) ‑> str</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Set the URL address for the JSON schema to be used for validating the STAC object.
    Validate new versions at schemas.stacspec.org</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>version</code></strong> :&ensp;<code>str</code></dt>
    <dd>The version number of the STAC object.</dd>
    <dt><strong><code>stac_type</code></strong> :&ensp;<code>str</code></dt>
    <dd>The type of the STAC object (e.g. "item", "collection").</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <dl>
    <dt><code>str</code></dt>
    <dd>The URL address for the JSON schema.</dd>
    </dl></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def set_schema_addr(version: str, stac_type: str) -&gt; str:
        &#34;&#34;&#34;Set the URL address for the JSON schema to be used for validating the STAC object.
        Validate new versions at schemas.stacspec.org

        Args:
            version (str): The version number of the STAC object.
            stac_type (str): The type of the STAC object (e.g. &#34;item&#34;, &#34;collection&#34;).

        Returns:
            str: The URL address for the JSON schema.
        &#34;&#34;&#34;
        if version in NEW_VERSIONS:
            return f&#34;https://schemas.stacspec.org/v{version}/{stac_type}-spec/json-schema/{stac_type}.json&#34;
        else:
            return f&#34;https://cdn.staclint.com/v{version}/{stac_type}.json&#34;</code></pre>
    </details>
    </dd>
    </dl>
    </section>
    <section>
    </section>
    </article>
    <nav id="sidebar">
    <h1>Index</h1>
    <div class="toc">
    <ul></ul>
    </div>
    <ul id="index">
    <li><h3>Super-module</h3>
    <ul>
    <li><code><a title="stac_validator" href="index.html">stac_validator</a></code></li>
    </ul>
    </li>
    <li><h3><a href="#header-functions">Functions</a></h3>
    <ul class="">
    <li><code><a title="stac_validator.utilities.fetch_and_parse_file" href="#stac_validator.utilities.fetch_and_parse_file">fetch_and_parse_file</a></code></li>
    <li><code><a title="stac_validator.utilities.fetch_and_parse_schema" href="#stac_validator.utilities.fetch_and_parse_schema">fetch_and_parse_schema</a></code></li>
    <li><code><a title="stac_validator.utilities.get_stac_type" href="#stac_validator.utilities.get_stac_type">get_stac_type</a></code></li>
    <li><code><a title="stac_validator.utilities.is_url" href="#stac_validator.utilities.is_url">is_url</a></code></li>
    <li><code><a title="stac_validator.utilities.is_valid_url" href="#stac_validator.utilities.is_valid_url">is_valid_url</a></code></li>
    <li><code><a title="stac_validator.utilities.link_request" href="#stac_validator.utilities.link_request">link_request</a></code></li>
    <li><code><a title="stac_validator.utilities.set_schema_addr" href="#stac_validator.utilities.set_schema_addr">set_schema_addr</a></code></li>
    </ul>
    </li>
    </ul>
    </nav>
    </main>
    <footer id="footer">
    <p>Generated by <a href="https://pdoc3.github.io/pdoc"><cite>pdoc</cite> 0.9.2</a>.</p>
    </footer>
    </body>
    </html>
    </embed>