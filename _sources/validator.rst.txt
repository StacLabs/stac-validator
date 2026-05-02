Validate API Reference
=======================

.. raw:: html

    <embed>
    <!doctype html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1" />
    <meta name="generator" content="pdoc 0.9.2" />
    <title>stac_validator.validate API documentation</title>
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
    <h1 class="title">Module <code>stac_validator.validate</code></h1>
    </header>
    <section id="section-intro">
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">import json
    import os
    from json.decoder import JSONDecodeError
    from typing import Optional
    from urllib.error import HTTPError, URLError

    import click  # type: ignore
    import jsonschema  # type: ignore
    from jsonschema import RefResolver
    from requests import exceptions  # type: ignore

    from .utilities import (
        fetch_and_parse_file,
        fetch_and_parse_schema,
        get_stac_type,
        is_valid_url,
        link_request,
        set_schema_addr,
    )


    class StacValidate:
        &#34;&#34;&#34;
        Class that validates STAC objects.

        Attributes:
            stac_file (str): The path or URL to the STAC object to be validated.
            item_collection (bool): Whether the STAC object to be validated is an item collection.
            pages (int): The maximum number of pages to validate if `item_collection` is True.
            recursive (bool): Whether to recursively validate related STAC objects.
            max_depth (int): The maximum depth to traverse when recursively validating related STAC objects.
            core (bool): Whether to only validate the core STAC object (without extensions).
            links (bool): Whether to additionally validate links (only works in default mode).
            assets (bool): Whether to additionally validate assets (only works in default mode).
            extensions (bool): Whether to only validate STAC object extensions.
            custom (str): The local filepath or remote URL of a custom JSON schema to validate the STAC object.
            verbose (bool): Whether to enable verbose output in recursive mode.
            log (str): The local filepath to save the output of the recursive validation to.

        Methods:
            run(): Validates the STAC object and returns whether it is valid.
            validate_item_collection(): Validates an item collection.
        &#34;&#34;&#34;

        def __init__(
            self,
            stac_file: Optional[str] = None,
            item_collection: bool = False,
            pages: Optional[int] = None,
            recursive: bool = False,
            max_depth: Optional[int] = None,
            core: bool = False,
            links: bool = False,
            assets: bool = False,
            extensions: bool = False,
            custom: str = &#34;&#34;,
            verbose: bool = False,
            log: str = &#34;&#34;,
        ):
            self.stac_file = stac_file
            self.item_collection = item_collection
            self.pages = pages
            self.message: list = []
            self.schema = custom
            self.links = links
            self.assets = assets
            self.recursive = recursive
            self.max_depth = max_depth
            self.extensions = extensions
            self.core = core
            self.stac_content: dict = {}
            self.version = &#34;&#34;
            self.depth: int = 0
            self.skip_val = False
            self.verbose = verbose
            self.valid = False
            self.log = log

        def create_err_msg(self, err_type: str, err_msg: str) -&gt; dict:
            self.valid = False
            return {
                &#34;version&#34;: self.version,
                &#34;path&#34;: self.stac_file,
                &#34;schema&#34;: [self.schema],
                &#34;valid_stac&#34;: False,
                &#34;error_type&#34;: err_type,
                &#34;error_message&#34;: err_msg,
            }

        def create_links_message(self):
            format_valid = []
            format_invalid = []
            request_valid = []
            request_invalid = []
            return {
                &#34;format_valid&#34;: format_valid,
                &#34;format_invalid&#34;: format_invalid,
                &#34;request_valid&#34;: request_valid,
                &#34;request_invalid&#34;: request_invalid,
            }

        def create_message(self, stac_type: str, val_type: str) -&gt; dict:
            return {
                &#34;version&#34;: self.version,
                &#34;path&#34;: self.stac_file,
                &#34;schema&#34;: [self.schema],
                &#34;valid_stac&#34;: False,
                &#34;asset_type&#34;: stac_type.upper(),
                &#34;validation_method&#34;: val_type,
            }

        def assets_validator(self) -&gt; dict:
            &#34;&#34;&#34;Validate assets.

            Returns:
                A dictionary containing the asset validation results.
            &#34;&#34;&#34;
            initial_message = self.create_links_message()
            assets = self.stac_content.get(&#34;assets&#34;)
            if assets:
                for asset in assets.values():
                    link_request(asset, initial_message)
            return initial_message

        def links_validator(self) -&gt; dict:
            &#34;&#34;&#34;Validate links.

            Returns:
                A dictionary containing the link validation results.
            &#34;&#34;&#34;
            initial_message = self.create_links_message()
            # get root_url for checking relative links
            root_url = &#34;&#34;
            for link in self.stac_content[&#34;links&#34;]:
                if link[&#34;rel&#34;] in [&#34;self&#34;, &#34;alternate&#34;] and is_valid_url(link[&#34;href&#34;]):
                    root_url = (
                        link[&#34;href&#34;].split(&#34;/&#34;)[0] + &#34;//&#34; + link[&#34;href&#34;].split(&#34;/&#34;)[2]
                    )
            for link in self.stac_content[&#34;links&#34;]:
                if not is_valid_url(link[&#34;href&#34;]):
                    link[&#34;href&#34;] = root_url + link[&#34;href&#34;][1:]
                link_request(link, initial_message)

            return initial_message

        def extensions_validator(self, stac_type: str) -&gt; dict:
            &#34;&#34;&#34;Validate the STAC extensions according to their corresponding JSON schemas.

            Args:
                stac_type (str): The STAC object type (&#34;ITEM&#34; or &#34;COLLECTION&#34;).

            Returns:
                dict: A dictionary containing validation results.

            Raises:
                JSONSchemaValidationError: If there is a validation error in the JSON schema.
                Exception: If there is an error in the STAC extension validation process.
            &#34;&#34;&#34;
            message = self.create_message(stac_type, &#34;extensions&#34;)
            message[&#34;schema&#34;] = []
            valid = True
            if stac_type == &#34;ITEM&#34;:
                try:
                    if &#34;stac_extensions&#34; in self.stac_content:
                        # error with the &#39;proj&#39; extension not being &#39;projection&#39; in older stac
                        if &#34;proj&#34; in self.stac_content[&#34;stac_extensions&#34;]:
                            index = self.stac_content[&#34;stac_extensions&#34;].index(&#34;proj&#34;)
                            self.stac_content[&#34;stac_extensions&#34;][index] = &#34;projection&#34;
                        schemas = self.stac_content[&#34;stac_extensions&#34;]
                        for extension in schemas:
                            if not (is_valid_url(extension) or extension.endswith(&#34;.json&#34;)):
                                # where are the extensions for 1.0.0-beta.2 on cdn.staclint.com?
                                if self.version == &#34;1.0.0-beta.2&#34;:
                                    self.stac_content[&#34;stac_version&#34;] = &#34;1.0.0-beta.1&#34;
                                    self.version = self.stac_content[&#34;stac_version&#34;]
                                extension = f&#34;https://cdn.staclint.com/v{self.version}/extension/{extension}.json&#34;
                            self.schema = extension
                            self.custom_validator()
                            message[&#34;schema&#34;].append(extension)
                except jsonschema.exceptions.ValidationError as e:
                    valid = False
                    if e.absolute_path:
                        err_msg = f&#34;{e.message}. Error is in {&#39; -&gt; &#39;.join([str(i) for i in e.absolute_path])}&#34;
                    else:
                        err_msg = f&#34;{e.message} of the root of the STAC object&#34;
                    message = self.create_err_msg(&#34;JSONSchemaValidationError&#34;, err_msg)
                    return message
                except Exception as e:
                    valid = False
                    err_msg = f&#34;{e}. Error in Extensions.&#34;
                    return self.create_err_msg(&#34;Exception&#34;, err_msg)
            else:
                self.core_validator(stac_type)
                message[&#34;schema&#34;] = [self.schema]
            self.valid = valid
            return message

        def custom_validator(self) -&gt; None:
            &#34;&#34;&#34;Validates a STAC JSON file against a JSON schema, which may be located
            either online or locally.

            The function checks whether the provided schema URL is valid and can be
            fetched and parsed. If the schema is hosted online, the function uses the
            fetched schema to validate the STAC JSON file. If the schema is local, the
            function resolves any references in the schema and then validates the STAC
            JSON file against the resolved schema. If the schema is specified as a
            relative path, the function resolves the path relative to the STAC JSON file
            being validated and uses the resolved schema to validate the STAC JSON file.

            Returns:
                None
            &#34;&#34;&#34;
            # if schema is hosted online
            if is_valid_url(self.schema):
                schema = fetch_and_parse_schema(self.schema)
                jsonschema.validate(self.stac_content, schema)
            # in case the path to a json schema is local
            elif os.path.exists(self.schema):
                schema = fetch_and_parse_schema(self.schema)
                custom_abspath = os.path.abspath(self.schema)
                custom_dir = os.path.dirname(custom_abspath).replace(&#34;\\&#34;, &#34;/&#34;)
                custom_uri = f&#34;file:///{custom_dir}/&#34;
                resolver = RefResolver(custom_uri, self.schema)
                jsonschema.validate(self.stac_content, schema, resolver=resolver)
            # deal with a relative path in the schema
            else:
                file_directory = os.path.dirname(os.path.abspath(str(self.stac_file)))
                self.schema = os.path.join(str(file_directory), self.schema)
                self.schema = os.path.abspath(os.path.realpath(self.schema))
                schema = fetch_and_parse_schema(self.schema)
                jsonschema.validate(self.stac_content, schema)

        def core_validator(self, stac_type: str) -&gt; None:
            &#34;&#34;&#34;Validate the STAC item or collection against the appropriate JSON schema.

            Args:
                stac_type (str): The type of STAC object being validated (either &#34;item&#34; or &#34;collection&#34;).

            Returns:
                None

            Raises:
                ValidationError: If the STAC object fails to validate against the JSON schema.

            The function first determines the appropriate JSON schema to use based on the STAC object&#39;s type and version.
            If the version is one of the specified versions (0.8.0, 0.9.0, 1.0.0, 1.0.0-beta.1, 1.0.0-beta.2, or 1.0.0-rc.2),
            it uses the corresponding schema stored locally. Otherwise, it retrieves the schema from the appropriate URL
            using the `set_schema_addr` function. The function then calls the `custom_validator` method to validate the
            STAC object against the schema.
            &#34;&#34;&#34;
            stac_type = stac_type.lower()
            self.schema = set_schema_addr(self.version, stac_type)
            self.custom_validator()

        def default_validator(self, stac_type: str) -&gt; dict:
            &#34;&#34;&#34;Validate the STAC catalog or item against the core schema and its extensions.

            Args:
                stac_type (str): The type of STAC object being validated. Must be either &#34;catalog&#34; or &#34;item&#34;.

            Returns:
                A dictionary containing the results of the default validation, including whether the STAC object is valid,
                any validation errors encountered, and any links and assets that were validated.
            &#34;&#34;&#34;
            message = self.create_message(stac_type, &#34;default&#34;)
            message[&#34;schema&#34;] = []
            self.core_validator(stac_type)
            core_schema = self.schema
            message[&#34;schema&#34;].append(core_schema)
            stac_type = stac_type.upper()
            if stac_type == &#34;ITEM&#34;:
                message = self.extensions_validator(stac_type)
                message[&#34;validation_method&#34;] = &#34;default&#34;
                message[&#34;schema&#34;].append(core_schema)
            if self.links:
                message[&#34;links_validated&#34;] = self.links_validator()
            if self.assets:
                message[&#34;assets_validated&#34;] = self.assets_validator()
            return message

        def recursive_validator(self, stac_type: str) -&gt; bool:
            &#34;&#34;&#34;Recursively validate a STAC JSON document against its JSON Schema.

            This method validates a STAC JSON document recursively against its JSON Schema by following its &#34;child&#34; and &#34;item&#34; links.
            It uses the `default_validator` and `fetch_and_parse_file` functions to validate the current STAC document and retrieve the
            next one to be validated, respectively.

            Args:
                self: An instance of the STACValidator class.
                stac_type: A string representing the STAC object type to validate.

            Returns:
                A boolean indicating whether the validation was successful.

            Raises:
                jsonschema.exceptions.ValidationError: If the STAC document does not validate against its JSON Schema.

            &#34;&#34;&#34;
            if self.skip_val is False:
                self.schema = set_schema_addr(self.version, stac_type.lower())
                message = self.create_message(stac_type, &#34;recursive&#34;)
                message[&#34;valid_stac&#34;] = False
                try:
                    _ = self.default_validator(stac_type)

                except jsonschema.exceptions.ValidationError as e:
                    if e.absolute_path:
                        err_msg = f&#34;{e.message}. Error is in {&#39; -&gt; &#39;.join([str(i) for i in e.absolute_path])}&#34;
                    else:
                        err_msg = f&#34;{e.message} of the root of the STAC object&#34;
                    message.update(
                        self.create_err_msg(&#34;JSONSchemaValidationError&#34;, err_msg)
                    )
                    self.message.append(message)
                    if self.verbose is True:
                        click.echo(json.dumps(message, indent=4))
                    return False

                message[&#34;valid_stac&#34;] = True
                self.message.append(message)
                if self.verbose:
                    click.echo(json.dumps(message, indent=4))
                self.depth += 1
                if self.max_depth and self.depth &gt;= self.max_depth:
                    self.skip_val = True
                base_url = self.stac_file

                for link in self.stac_content[&#34;links&#34;]:
                    if link[&#34;rel&#34;] == &#34;child&#34; or link[&#34;rel&#34;] == &#34;item&#34;:
                        address = link[&#34;href&#34;]
                        if not is_valid_url(address):
                            x = str(base_url).split(&#34;/&#34;)
                            x.pop(-1)
                            st = x[0]
                            for i in range(len(x)):
                                if i &gt; 0:
                                    st = st + &#34;/&#34; + x[i]
                            self.stac_file = st + &#34;/&#34; + address
                        else:
                            self.stac_file = address
                        self.stac_content = fetch_and_parse_file(str(self.stac_file))
                        self.stac_content[&#34;stac_version&#34;] = self.version
                        stac_type = get_stac_type(self.stac_content).lower()

                    if link[&#34;rel&#34;] == &#34;child&#34;:
                        self.recursive_validator(stac_type)

                    if link[&#34;rel&#34;] == &#34;item&#34;:
                        self.schema = set_schema_addr(self.version, stac_type.lower())
                        message = self.create_message(stac_type, &#34;recursive&#34;)
                        if self.version == &#34;0.7.0&#34;:
                            schema = fetch_and_parse_schema(self.schema)
                            # this next line prevents this: unknown url type: &#39;geojson.json&#39; ??
                            schema[&#34;allOf&#34;] = [{}]
                            jsonschema.validate(self.stac_content, schema)
                        else:
                            msg = self.default_validator(stac_type)
                            message[&#34;schema&#34;] = msg[&#34;schema&#34;]
                        message[&#34;valid_stac&#34;] = True

                        if self.log != &#34;&#34;:
                            self.message.append(message)
                        if (
                            not self.max_depth or self.max_depth &lt; 5
                        ):  # TODO this should be configurable, correct?
                            self.message.append(message)
            return True

        def validate_dict(self, stac_content) -&gt; bool:
            &#34;&#34;&#34;Validate the contents of a dictionary representing a STAC object.

            Args:
                stac_content (dict): The dictionary representation of the STAC object to validate.

            Returns:
                A bool indicating if validation was successfull.
            &#34;&#34;&#34;
            self.stac_content = stac_content
            return self.run()

        def validate_item_collection_dict(self, item_collection: dict) -&gt; None:
            &#34;&#34;&#34;Validate the contents of an item collection.

            Args:
                item_collection (dict): The dictionary representation of the item collection to validate.

            Returns:
                None
            &#34;&#34;&#34;
            for item in item_collection[&#34;features&#34;]:
                self.schema = &#34;&#34;
                self.validate_dict(item)

        def validate_item_collection(self) -&gt; None:
            &#34;&#34;&#34;Validate a STAC item collection.

            Raises:
                URLError: If there is an issue with the URL used to fetch the item collection.
                JSONDecodeError: If the item collection content cannot be parsed as JSON.
                ValueError: If the item collection does not conform to the STAC specification.
                TypeError: If the item collection content is not a dictionary or JSON object.
                FileNotFoundError: If the item collection file cannot be found.
                ConnectionError: If there is an issue with the internet connection used to fetch the item collection.
                exceptions.SSLError: If there is an issue with the SSL connection used to fetch the item collection.
                OSError: If there is an issue with the file system (e.g., read/write permissions) while trying to write to the log file.

            Returns:
                None
            &#34;&#34;&#34;
            page = 1
            print(f&#34;processing page {page}&#34;)
            item_collection = fetch_and_parse_file(str(self.stac_file))
            self.validate_item_collection_dict(item_collection)
            try:
                if self.pages is not None:
                    for _ in range(self.pages - 1):
                        if &#34;links&#34; in item_collection:
                            for link in item_collection[&#34;links&#34;]:
                                if link[&#34;rel&#34;] == &#34;next&#34;:
                                    page = page + 1
                                    print(f&#34;processing page {page}&#34;)
                                    next_link = link[&#34;href&#34;]
                                    self.stac_file = next_link
                                    item_collection = fetch_and_parse_file(
                                        str(self.stac_file)
                                    )
                                    self.validate_item_collection_dict(item_collection)
                                    break
            except Exception as e:
                message = {}
                message[
                    &#34;pagination_error&#34;
                ] = f&#34;Validating the item collection failed on page {page}: {str(e)}&#34;
                self.message.append(message)

        def run(self) -&gt; bool:
            &#34;&#34;&#34;Runs the STAC validation process based on the input parameters.

            Returns:
                bool: True if the STAC is valid, False otherwise.

            Raises:
                URLError: If there is an error with the URL.
                JSONDecodeError: If there is an error decoding the JSON content.
                ValueError: If there is an invalid value.
                TypeError: If there is an invalid type.
                FileNotFoundError: If the file is not found.
                ConnectionError: If there is an error with the connection.
                exceptions.SSLError: If there is an SSL error.
                OSError: If there is an error with the operating system.
                jsonschema.exceptions.ValidationError: If the STAC content fails validation.
                KeyError: If the specified key is not found.
                HTTPError: If there is an error with the HTTP connection.
                Exception: If there is any other type of error.

            &#34;&#34;&#34;
            message = {}
            try:
                if self.stac_file is not None and not self.item_collection:
                    self.stac_content = fetch_and_parse_file(self.stac_file)

                stac_type = get_stac_type(self.stac_content).upper()
                self.version = self.stac_content[&#34;stac_version&#34;]

                if self.core:
                    message = self.create_message(stac_type, &#34;core&#34;)
                    self.core_validator(stac_type)
                    message[&#34;schema&#34;] = [self.schema]
                    self.valid = True
                elif self.schema != &#34;&#34;:
                    message = self.create_message(stac_type, &#34;custom&#34;)
                    message[&#34;schema&#34;] = [self.schema]
                    self.custom_validator()
                    self.valid = True
                elif self.recursive:
                    self.valid = self.recursive_validator(stac_type)
                elif self.extensions:
                    message = self.extensions_validator(stac_type)
                else:
                    self.valid = True
                    message = self.default_validator(stac_type)

            except jsonschema.exceptions.ValidationError as e:
                if e.absolute_path:
                    err_msg = f&#34;{e.message}. Error is in {&#39; -&gt; &#39;.join([str(i) for i in e.absolute_path])} &#34;
                else:
                    err_msg = f&#34;{e.message} of the root of the STAC object&#34;
                message.update(self.create_err_msg(&#34;JSONSchemaValidationError&#34;, err_msg))

            except (
                URLError,
                JSONDecodeError,
                ValueError,
                TypeError,
                FileNotFoundError,
                ConnectionError,
                exceptions.SSLError,
                OSError,
                KeyError,
                HTTPError,
            ) as e:
                message.update(self.create_err_msg(type(e).__name__, str(e)))

            except Exception as e:
                message.update(self.create_err_msg(&#34;Exception&#34;, str(e)))

            if message:
                message[&#34;valid_stac&#34;] = self.valid
                self.message.append(message)

            if self.log != &#34;&#34;:
                with open(self.log, &#34;w&#34;) as f:
                    f.write(json.dumps(self.message, indent=4))

            return self.valid</code></pre>
    </details>
    </section>
    <section>
    </section>
    <section>
    </section>
    <section>
    </section>
    <section>
    <h2 class="section-title" id="header-classes">Classes</h2>
    <dl>
    <dt id="stac_validator.validate.StacValidate"><code class="flex name class">
    <span>class <span class="ident">StacValidate</span></span>
    <span>(</span><span>stac_file: Optional[str] = None, item_collection: bool = False, pages: Optional[int] = None, recursive: bool = False, max_depth: Optional[int] = None, core: bool = False, links: bool = False, assets: bool = False, extensions: bool = False, custom: str = '', verbose: bool = False, log: str = '')</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Class that validates STAC objects.</p>
    <h2 id="attributes">Attributes</h2>
    <dl>
    <dt><strong><code>stac_file</code></strong> :&ensp;<code>str</code></dt>
    <dd>The path or URL to the STAC object to be validated.</dd>
    <dt><strong><code>item_collection</code></strong> :&ensp;<code>bool</code></dt>
    <dd>Whether the STAC object to be validated is an item collection.</dd>
    <dt><strong><code>pages</code></strong> :&ensp;<code>int</code></dt>
    <dd>The maximum number of pages to validate if <code>item_collection</code> is True.</dd>
    <dt><strong><code>recursive</code></strong> :&ensp;<code>bool</code></dt>
    <dd>Whether to recursively validate related STAC objects.</dd>
    <dt><strong><code>max_depth</code></strong> :&ensp;<code>int</code></dt>
    <dd>The maximum depth to traverse when recursively validating related STAC objects.</dd>
    <dt><strong><code>core</code></strong> :&ensp;<code>bool</code></dt>
    <dd>Whether to only validate the core STAC object (without extensions).</dd>
    <dt><strong><code>links</code></strong> :&ensp;<code>bool</code></dt>
    <dd>Whether to additionally validate links (only works in default mode).</dd>
    <dt><strong><code>assets</code></strong> :&ensp;<code>bool</code></dt>
    <dd>Whether to additionally validate assets (only works in default mode).</dd>
    <dt><strong><code>extensions</code></strong> :&ensp;<code>bool</code></dt>
    <dd>Whether to only validate STAC object extensions.</dd>
    <dt><strong><code>custom</code></strong> :&ensp;<code>str</code></dt>
    <dd>The local filepath or remote URL of a custom JSON schema to validate the STAC object.</dd>
    <dt><strong><code>verbose</code></strong> :&ensp;<code>bool</code></dt>
    <dd>Whether to enable verbose output in recursive mode.</dd>
    <dt><strong><code>log</code></strong> :&ensp;<code>str</code></dt>
    <dd>The local filepath to save the output of the recursive validation to.</dd>
    </dl>
    <h2 id="methods">Methods</h2>
    <p>run(): Validates the STAC object and returns whether it is valid.
    validate_item_collection(): Validates an item collection.</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">class StacValidate:
        &#34;&#34;&#34;
        Class that validates STAC objects.

        Attributes:
            stac_file (str): The path or URL to the STAC object to be validated.
            item_collection (bool): Whether the STAC object to be validated is an item collection.
            pages (int): The maximum number of pages to validate if `item_collection` is True.
            recursive (bool): Whether to recursively validate related STAC objects.
            max_depth (int): The maximum depth to traverse when recursively validating related STAC objects.
            core (bool): Whether to only validate the core STAC object (without extensions).
            links (bool): Whether to additionally validate links (only works in default mode).
            assets (bool): Whether to additionally validate assets (only works in default mode).
            extensions (bool): Whether to only validate STAC object extensions.
            custom (str): The local filepath or remote URL of a custom JSON schema to validate the STAC object.
            verbose (bool): Whether to enable verbose output in recursive mode.
            log (str): The local filepath to save the output of the recursive validation to.

        Methods:
            run(): Validates the STAC object and returns whether it is valid.
            validate_item_collection(): Validates an item collection.
        &#34;&#34;&#34;

        def __init__(
            self,
            stac_file: Optional[str] = None,
            item_collection: bool = False,
            pages: Optional[int] = None,
            recursive: bool = False,
            max_depth: Optional[int] = None,
            core: bool = False,
            links: bool = False,
            assets: bool = False,
            extensions: bool = False,
            custom: str = &#34;&#34;,
            verbose: bool = False,
            log: str = &#34;&#34;,
        ):
            self.stac_file = stac_file
            self.item_collection = item_collection
            self.pages = pages
            self.message: list = []
            self.schema = custom
            self.links = links
            self.assets = assets
            self.recursive = recursive
            self.max_depth = max_depth
            self.extensions = extensions
            self.core = core
            self.stac_content: dict = {}
            self.version = &#34;&#34;
            self.depth: int = 0
            self.skip_val = False
            self.verbose = verbose
            self.valid = False
            self.log = log

        def create_err_msg(self, err_type: str, err_msg: str) -&gt; dict:
            self.valid = False
            return {
                &#34;version&#34;: self.version,
                &#34;path&#34;: self.stac_file,
                &#34;schema&#34;: [self.schema],
                &#34;valid_stac&#34;: False,
                &#34;error_type&#34;: err_type,
                &#34;error_message&#34;: err_msg,
            }

        def create_links_message(self):
            format_valid = []
            format_invalid = []
            request_valid = []
            request_invalid = []
            return {
                &#34;format_valid&#34;: format_valid,
                &#34;format_invalid&#34;: format_invalid,
                &#34;request_valid&#34;: request_valid,
                &#34;request_invalid&#34;: request_invalid,
            }

        def create_message(self, stac_type: str, val_type: str) -&gt; dict:
            return {
                &#34;version&#34;: self.version,
                &#34;path&#34;: self.stac_file,
                &#34;schema&#34;: [self.schema],
                &#34;valid_stac&#34;: False,
                &#34;asset_type&#34;: stac_type.upper(),
                &#34;validation_method&#34;: val_type,
            }

        def assets_validator(self) -&gt; dict:
            &#34;&#34;&#34;Validate assets.

            Returns:
                A dictionary containing the asset validation results.
            &#34;&#34;&#34;
            initial_message = self.create_links_message()
            assets = self.stac_content.get(&#34;assets&#34;)
            if assets:
                for asset in assets.values():
                    link_request(asset, initial_message)
            return initial_message

        def links_validator(self) -&gt; dict:
            &#34;&#34;&#34;Validate links.

            Returns:
                A dictionary containing the link validation results.
            &#34;&#34;&#34;
            initial_message = self.create_links_message()
            # get root_url for checking relative links
            root_url = &#34;&#34;
            for link in self.stac_content[&#34;links&#34;]:
                if link[&#34;rel&#34;] in [&#34;self&#34;, &#34;alternate&#34;] and is_valid_url(link[&#34;href&#34;]):
                    root_url = (
                        link[&#34;href&#34;].split(&#34;/&#34;)[0] + &#34;//&#34; + link[&#34;href&#34;].split(&#34;/&#34;)[2]
                    )
            for link in self.stac_content[&#34;links&#34;]:
                if not is_valid_url(link[&#34;href&#34;]):
                    link[&#34;href&#34;] = root_url + link[&#34;href&#34;][1:]
                link_request(link, initial_message)

            return initial_message

        def extensions_validator(self, stac_type: str) -&gt; dict:
            &#34;&#34;&#34;Validate the STAC extensions according to their corresponding JSON schemas.

            Args:
                stac_type (str): The STAC object type (&#34;ITEM&#34; or &#34;COLLECTION&#34;).

            Returns:
                dict: A dictionary containing validation results.

            Raises:
                JSONSchemaValidationError: If there is a validation error in the JSON schema.
                Exception: If there is an error in the STAC extension validation process.
            &#34;&#34;&#34;
            message = self.create_message(stac_type, &#34;extensions&#34;)
            message[&#34;schema&#34;] = []
            valid = True
            if stac_type == &#34;ITEM&#34;:
                try:
                    if &#34;stac_extensions&#34; in self.stac_content:
                        # error with the &#39;proj&#39; extension not being &#39;projection&#39; in older stac
                        if &#34;proj&#34; in self.stac_content[&#34;stac_extensions&#34;]:
                            index = self.stac_content[&#34;stac_extensions&#34;].index(&#34;proj&#34;)
                            self.stac_content[&#34;stac_extensions&#34;][index] = &#34;projection&#34;
                        schemas = self.stac_content[&#34;stac_extensions&#34;]
                        for extension in schemas:
                            if not (is_valid_url(extension) or extension.endswith(&#34;.json&#34;)):
                                # where are the extensions for 1.0.0-beta.2 on cdn.staclint.com?
                                if self.version == &#34;1.0.0-beta.2&#34;:
                                    self.stac_content[&#34;stac_version&#34;] = &#34;1.0.0-beta.1&#34;
                                    self.version = self.stac_content[&#34;stac_version&#34;]
                                extension = f&#34;https://cdn.staclint.com/v{self.version}/extension/{extension}.json&#34;
                            self.schema = extension
                            self.custom_validator()
                            message[&#34;schema&#34;].append(extension)
                except jsonschema.exceptions.ValidationError as e:
                    valid = False
                    if e.absolute_path:
                        err_msg = f&#34;{e.message}. Error is in {&#39; -&gt; &#39;.join([str(i) for i in e.absolute_path])}&#34;
                    else:
                        err_msg = f&#34;{e.message} of the root of the STAC object&#34;
                    message = self.create_err_msg(&#34;JSONSchemaValidationError&#34;, err_msg)
                    return message
                except Exception as e:
                    valid = False
                    err_msg = f&#34;{e}. Error in Extensions.&#34;
                    return self.create_err_msg(&#34;Exception&#34;, err_msg)
            else:
                self.core_validator(stac_type)
                message[&#34;schema&#34;] = [self.schema]
            self.valid = valid
            return message

        def custom_validator(self) -&gt; None:
            &#34;&#34;&#34;Validates a STAC JSON file against a JSON schema, which may be located
            either online or locally.

            The function checks whether the provided schema URL is valid and can be
            fetched and parsed. If the schema is hosted online, the function uses the
            fetched schema to validate the STAC JSON file. If the schema is local, the
            function resolves any references in the schema and then validates the STAC
            JSON file against the resolved schema. If the schema is specified as a
            relative path, the function resolves the path relative to the STAC JSON file
            being validated and uses the resolved schema to validate the STAC JSON file.

            Returns:
                None
            &#34;&#34;&#34;
            # if schema is hosted online
            if is_valid_url(self.schema):
                schema = fetch_and_parse_schema(self.schema)
                jsonschema.validate(self.stac_content, schema)
            # in case the path to a json schema is local
            elif os.path.exists(self.schema):
                schema = fetch_and_parse_schema(self.schema)
                custom_abspath = os.path.abspath(self.schema)
                custom_dir = os.path.dirname(custom_abspath).replace(&#34;\\&#34;, &#34;/&#34;)
                custom_uri = f&#34;file:///{custom_dir}/&#34;
                resolver = RefResolver(custom_uri, self.schema)
                jsonschema.validate(self.stac_content, schema, resolver=resolver)
            # deal with a relative path in the schema
            else:
                file_directory = os.path.dirname(os.path.abspath(str(self.stac_file)))
                self.schema = os.path.join(str(file_directory), self.schema)
                self.schema = os.path.abspath(os.path.realpath(self.schema))
                schema = fetch_and_parse_schema(self.schema)
                jsonschema.validate(self.stac_content, schema)

        def core_validator(self, stac_type: str) -&gt; None:
            &#34;&#34;&#34;Validate the STAC item or collection against the appropriate JSON schema.

            Args:
                stac_type (str): The type of STAC object being validated (either &#34;item&#34; or &#34;collection&#34;).

            Returns:
                None

            Raises:
                ValidationError: If the STAC object fails to validate against the JSON schema.

            The function first determines the appropriate JSON schema to use based on the STAC object&#39;s type and version.
            If the version is one of the specified versions (0.8.0, 0.9.0, 1.0.0, 1.0.0-beta.1, 1.0.0-beta.2, or 1.0.0-rc.2),
            it uses the corresponding schema stored locally. Otherwise, it retrieves the schema from the appropriate URL
            using the `set_schema_addr` function. The function then calls the `custom_validator` method to validate the
            STAC object against the schema.
            &#34;&#34;&#34;
            stac_type = stac_type.lower()
            self.schema = set_schema_addr(self.version, stac_type)
            self.custom_validator()

        def default_validator(self, stac_type: str) -&gt; dict:
            &#34;&#34;&#34;Validate the STAC catalog or item against the core schema and its extensions.

            Args:
                stac_type (str): The type of STAC object being validated. Must be either &#34;catalog&#34; or &#34;item&#34;.

            Returns:
                A dictionary containing the results of the default validation, including whether the STAC object is valid,
                any validation errors encountered, and any links and assets that were validated.
            &#34;&#34;&#34;
            message = self.create_message(stac_type, &#34;default&#34;)
            message[&#34;schema&#34;] = []
            self.core_validator(stac_type)
            core_schema = self.schema
            message[&#34;schema&#34;].append(core_schema)
            stac_type = stac_type.upper()
            if stac_type == &#34;ITEM&#34;:
                message = self.extensions_validator(stac_type)
                message[&#34;validation_method&#34;] = &#34;default&#34;
                message[&#34;schema&#34;].append(core_schema)
            if self.links:
                message[&#34;links_validated&#34;] = self.links_validator()
            if self.assets:
                message[&#34;assets_validated&#34;] = self.assets_validator()
            return message

        def recursive_validator(self, stac_type: str) -&gt; bool:
            &#34;&#34;&#34;Recursively validate a STAC JSON document against its JSON Schema.

            This method validates a STAC JSON document recursively against its JSON Schema by following its &#34;child&#34; and &#34;item&#34; links.
            It uses the `default_validator` and `fetch_and_parse_file` functions to validate the current STAC document and retrieve the
            next one to be validated, respectively.

            Args:
                self: An instance of the STACValidator class.
                stac_type: A string representing the STAC object type to validate.

            Returns:
                A boolean indicating whether the validation was successful.

            Raises:
                jsonschema.exceptions.ValidationError: If the STAC document does not validate against its JSON Schema.

            &#34;&#34;&#34;
            if self.skip_val is False:
                self.schema = set_schema_addr(self.version, stac_type.lower())
                message = self.create_message(stac_type, &#34;recursive&#34;)
                message[&#34;valid_stac&#34;] = False
                try:
                    _ = self.default_validator(stac_type)

                except jsonschema.exceptions.ValidationError as e:
                    if e.absolute_path:
                        err_msg = f&#34;{e.message}. Error is in {&#39; -&gt; &#39;.join([str(i) for i in e.absolute_path])}&#34;
                    else:
                        err_msg = f&#34;{e.message} of the root of the STAC object&#34;
                    message.update(
                        self.create_err_msg(&#34;JSONSchemaValidationError&#34;, err_msg)
                    )
                    self.message.append(message)
                    if self.verbose is True:
                        click.echo(json.dumps(message, indent=4))
                    return False

                message[&#34;valid_stac&#34;] = True
                self.message.append(message)
                if self.verbose:
                    click.echo(json.dumps(message, indent=4))
                self.depth += 1
                if self.max_depth and self.depth &gt;= self.max_depth:
                    self.skip_val = True
                base_url = self.stac_file

                for link in self.stac_content[&#34;links&#34;]:
                    if link[&#34;rel&#34;] == &#34;child&#34; or link[&#34;rel&#34;] == &#34;item&#34;:
                        address = link[&#34;href&#34;]
                        if not is_valid_url(address):
                            x = str(base_url).split(&#34;/&#34;)
                            x.pop(-1)
                            st = x[0]
                            for i in range(len(x)):
                                if i &gt; 0:
                                    st = st + &#34;/&#34; + x[i]
                            self.stac_file = st + &#34;/&#34; + address
                        else:
                            self.stac_file = address
                        self.stac_content = fetch_and_parse_file(str(self.stac_file))
                        self.stac_content[&#34;stac_version&#34;] = self.version
                        stac_type = get_stac_type(self.stac_content).lower()

                    if link[&#34;rel&#34;] == &#34;child&#34;:
                        self.recursive_validator(stac_type)

                    if link[&#34;rel&#34;] == &#34;item&#34;:
                        self.schema = set_schema_addr(self.version, stac_type.lower())
                        message = self.create_message(stac_type, &#34;recursive&#34;)
                        if self.version == &#34;0.7.0&#34;:
                            schema = fetch_and_parse_schema(self.schema)
                            # this next line prevents this: unknown url type: &#39;geojson.json&#39; ??
                            schema[&#34;allOf&#34;] = [{}]
                            jsonschema.validate(self.stac_content, schema)
                        else:
                            msg = self.default_validator(stac_type)
                            message[&#34;schema&#34;] = msg[&#34;schema&#34;]
                        message[&#34;valid_stac&#34;] = True

                        if self.log != &#34;&#34;:
                            self.message.append(message)
                        if (
                            not self.max_depth or self.max_depth &lt; 5
                        ):  # TODO this should be configurable, correct?
                            self.message.append(message)
            return True

        def validate_dict(self, stac_content) -&gt; bool:
            &#34;&#34;&#34;Validate the contents of a dictionary representing a STAC object.

            Args:
                stac_content (dict): The dictionary representation of the STAC object to validate.

            Returns:
                A bool indicating if validation was successfull.
            &#34;&#34;&#34;
            self.stac_content = stac_content
            return self.run()

        def validate_item_collection_dict(self, item_collection: dict) -&gt; None:
            &#34;&#34;&#34;Validate the contents of an item collection.

            Args:
                item_collection (dict): The dictionary representation of the item collection to validate.

            Returns:
                None
            &#34;&#34;&#34;
            for item in item_collection[&#34;features&#34;]:
                self.schema = &#34;&#34;
                self.validate_dict(item)

        def validate_item_collection(self) -&gt; None:
            &#34;&#34;&#34;Validate a STAC item collection.

            Raises:
                URLError: If there is an issue with the URL used to fetch the item collection.
                JSONDecodeError: If the item collection content cannot be parsed as JSON.
                ValueError: If the item collection does not conform to the STAC specification.
                TypeError: If the item collection content is not a dictionary or JSON object.
                FileNotFoundError: If the item collection file cannot be found.
                ConnectionError: If there is an issue with the internet connection used to fetch the item collection.
                exceptions.SSLError: If there is an issue with the SSL connection used to fetch the item collection.
                OSError: If there is an issue with the file system (e.g., read/write permissions) while trying to write to the log file.

            Returns:
                None
            &#34;&#34;&#34;
            page = 1
            print(f&#34;processing page {page}&#34;)
            item_collection = fetch_and_parse_file(str(self.stac_file))
            self.validate_item_collection_dict(item_collection)
            try:
                if self.pages is not None:
                    for _ in range(self.pages - 1):
                        if &#34;links&#34; in item_collection:
                            for link in item_collection[&#34;links&#34;]:
                                if link[&#34;rel&#34;] == &#34;next&#34;:
                                    page = page + 1
                                    print(f&#34;processing page {page}&#34;)
                                    next_link = link[&#34;href&#34;]
                                    self.stac_file = next_link
                                    item_collection = fetch_and_parse_file(
                                        str(self.stac_file)
                                    )
                                    self.validate_item_collection_dict(item_collection)
                                    break
            except Exception as e:
                message = {}
                message[
                    &#34;pagination_error&#34;
                ] = f&#34;Validating the item collection failed on page {page}: {str(e)}&#34;
                self.message.append(message)

        def run(self) -&gt; bool:
            &#34;&#34;&#34;Runs the STAC validation process based on the input parameters.

            Returns:
                bool: True if the STAC is valid, False otherwise.

            Raises:
                URLError: If there is an error with the URL.
                JSONDecodeError: If there is an error decoding the JSON content.
                ValueError: If there is an invalid value.
                TypeError: If there is an invalid type.
                FileNotFoundError: If the file is not found.
                ConnectionError: If there is an error with the connection.
                exceptions.SSLError: If there is an SSL error.
                OSError: If there is an error with the operating system.
                jsonschema.exceptions.ValidationError: If the STAC content fails validation.
                KeyError: If the specified key is not found.
                HTTPError: If there is an error with the HTTP connection.
                Exception: If there is any other type of error.

            &#34;&#34;&#34;
            message = {}
            try:
                if self.stac_file is not None and not self.item_collection:
                    self.stac_content = fetch_and_parse_file(self.stac_file)

                stac_type = get_stac_type(self.stac_content).upper()
                self.version = self.stac_content[&#34;stac_version&#34;]

                if self.core:
                    message = self.create_message(stac_type, &#34;core&#34;)
                    self.core_validator(stac_type)
                    message[&#34;schema&#34;] = [self.schema]
                    self.valid = True
                elif self.schema != &#34;&#34;:
                    message = self.create_message(stac_type, &#34;custom&#34;)
                    message[&#34;schema&#34;] = [self.schema]
                    self.custom_validator()
                    self.valid = True
                elif self.recursive:
                    self.valid = self.recursive_validator(stac_type)
                elif self.extensions:
                    message = self.extensions_validator(stac_type)
                else:
                    self.valid = True
                    message = self.default_validator(stac_type)

            except jsonschema.exceptions.ValidationError as e:
                if e.absolute_path:
                    err_msg = f&#34;{e.message}. Error is in {&#39; -&gt; &#39;.join([str(i) for i in e.absolute_path])} &#34;
                else:
                    err_msg = f&#34;{e.message} of the root of the STAC object&#34;
                message.update(self.create_err_msg(&#34;JSONSchemaValidationError&#34;, err_msg))

            except (
                URLError,
                JSONDecodeError,
                ValueError,
                TypeError,
                FileNotFoundError,
                ConnectionError,
                exceptions.SSLError,
                OSError,
                KeyError,
                HTTPError,
            ) as e:
                message.update(self.create_err_msg(type(e).__name__, str(e)))

            except Exception as e:
                message.update(self.create_err_msg(&#34;Exception&#34;, str(e)))

            if message:
                message[&#34;valid_stac&#34;] = self.valid
                self.message.append(message)

            if self.log != &#34;&#34;:
                with open(self.log, &#34;w&#34;) as f:
                    f.write(json.dumps(self.message, indent=4))

            return self.valid</code></pre>
    </details>
    <h3>Methods</h3>
    <dl>
    <dt id="stac_validator.validate.StacValidate.assets_validator"><code class="name flex">
    <span>def <span class="ident">assets_validator</span></span>(<span>self) ‑> dict</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Validate assets.</p>
    <h2 id="returns">Returns</h2>
    <p>A dictionary containing the asset validation results.</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def assets_validator(self) -&gt; dict:
        &#34;&#34;&#34;Validate assets.

        Returns:
            A dictionary containing the asset validation results.
        &#34;&#34;&#34;
        initial_message = self.create_links_message()
        assets = self.stac_content.get(&#34;assets&#34;)
        if assets:
            for asset in assets.values():
                link_request(asset, initial_message)
        return initial_message</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.core_validator"><code class="name flex">
    <span>def <span class="ident">core_validator</span></span>(<span>self, stac_type: str) ‑> NoneType</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Validate the STAC item or collection against the appropriate JSON schema.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>stac_type</code></strong> :&ensp;<code>str</code></dt>
    <dd>The type of STAC object being validated (either "item" or "collection").</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>None</p>
    <h2 id="raises">Raises</h2>
    <dl>
    <dt><code>ValidationError</code></dt>
    <dd>If the STAC object fails to validate against the JSON schema.</dd>
    </dl>
    <p>The function first determines the appropriate JSON schema to use based on the STAC object's type and version.
    If the version is one of the specified versions (0.8.0, 0.9.0, 1.0.0, 1.0.0-beta.1, 1.0.0-beta.2, or 1.0.0-rc.2),
    it uses the corresponding schema stored locally. Otherwise, it retrieves the schema from the appropriate URL
    using the <code>set_schema_addr</code> function. The function then calls the <code>custom_validator</code> method to validate the
    STAC object against the schema.</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def core_validator(self, stac_type: str) -&gt; None:
        &#34;&#34;&#34;Validate the STAC item or collection against the appropriate JSON schema.

        Args:
            stac_type (str): The type of STAC object being validated (either &#34;item&#34; or &#34;collection&#34;).

        Returns:
            None

        Raises:
            ValidationError: If the STAC object fails to validate against the JSON schema.

        The function first determines the appropriate JSON schema to use based on the STAC object&#39;s type and version.
        If the version is one of the specified versions (0.8.0, 0.9.0, 1.0.0, 1.0.0-beta.1, 1.0.0-beta.2, or 1.0.0-rc.2),
        it uses the corresponding schema stored locally. Otherwise, it retrieves the schema from the appropriate URL
        using the `set_schema_addr` function. The function then calls the `custom_validator` method to validate the
        STAC object against the schema.
        &#34;&#34;&#34;
        stac_type = stac_type.lower()
        self.schema = set_schema_addr(self.version, stac_type)
        self.custom_validator()</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.create_err_msg"><code class="name flex">
    <span>def <span class="ident">create_err_msg</span></span>(<span>self, err_type: str, err_msg: str) ‑> dict</span>
    </code></dt>
    <dd>
    <div class="desc"></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def create_err_msg(self, err_type: str, err_msg: str) -&gt; dict:
        self.valid = False
        return {
            &#34;version&#34;: self.version,
            &#34;path&#34;: self.stac_file,
            &#34;schema&#34;: [self.schema],
            &#34;valid_stac&#34;: False,
            &#34;error_type&#34;: err_type,
            &#34;error_message&#34;: err_msg,
        }</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.create_links_message"><code class="name flex">
    <span>def <span class="ident">create_links_message</span></span>(<span>self)</span>
    </code></dt>
    <dd>
    <div class="desc"></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def create_links_message(self):
        format_valid = []
        format_invalid = []
        request_valid = []
        request_invalid = []
        return {
            &#34;format_valid&#34;: format_valid,
            &#34;format_invalid&#34;: format_invalid,
            &#34;request_valid&#34;: request_valid,
            &#34;request_invalid&#34;: request_invalid,
        }</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.create_message"><code class="name flex">
    <span>def <span class="ident">create_message</span></span>(<span>self, stac_type: str, val_type: str) ‑> dict</span>
    </code></dt>
    <dd>
    <div class="desc"></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def create_message(self, stac_type: str, val_type: str) -&gt; dict:
        return {
            &#34;version&#34;: self.version,
            &#34;path&#34;: self.stac_file,
            &#34;schema&#34;: [self.schema],
            &#34;valid_stac&#34;: False,
            &#34;asset_type&#34;: stac_type.upper(),
            &#34;validation_method&#34;: val_type,
        }</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.custom_validator"><code class="name flex">
    <span>def <span class="ident">custom_validator</span></span>(<span>self) ‑> NoneType</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Validates a STAC JSON file against a JSON schema, which may be located
    either online or locally.</p>
    <p>The function checks whether the provided schema URL is valid and can be
    fetched and parsed. If the schema is hosted online, the function uses the
    fetched schema to validate the STAC JSON file. If the schema is local, the
    function resolves any references in the schema and then validates the STAC
    JSON file against the resolved schema. If the schema is specified as a
    relative path, the function resolves the path relative to the STAC JSON file
    being validated and uses the resolved schema to validate the STAC JSON file.</p>
    <h2 id="returns">Returns</h2>
    <p>None</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def custom_validator(self) -&gt; None:
        &#34;&#34;&#34;Validates a STAC JSON file against a JSON schema, which may be located
        either online or locally.

        The function checks whether the provided schema URL is valid and can be
        fetched and parsed. If the schema is hosted online, the function uses the
        fetched schema to validate the STAC JSON file. If the schema is local, the
        function resolves any references in the schema and then validates the STAC
        JSON file against the resolved schema. If the schema is specified as a
        relative path, the function resolves the path relative to the STAC JSON file
        being validated and uses the resolved schema to validate the STAC JSON file.

        Returns:
            None
        &#34;&#34;&#34;
        # if schema is hosted online
        if is_valid_url(self.schema):
            schema = fetch_and_parse_schema(self.schema)
            jsonschema.validate(self.stac_content, schema)
        # in case the path to a json schema is local
        elif os.path.exists(self.schema):
            schema = fetch_and_parse_schema(self.schema)
            custom_abspath = os.path.abspath(self.schema)
            custom_dir = os.path.dirname(custom_abspath).replace(&#34;\\&#34;, &#34;/&#34;)
            custom_uri = f&#34;file:///{custom_dir}/&#34;
            resolver = RefResolver(custom_uri, self.schema)
            jsonschema.validate(self.stac_content, schema, resolver=resolver)
        # deal with a relative path in the schema
        else:
            file_directory = os.path.dirname(os.path.abspath(str(self.stac_file)))
            self.schema = os.path.join(str(file_directory), self.schema)
            self.schema = os.path.abspath(os.path.realpath(self.schema))
            schema = fetch_and_parse_schema(self.schema)
            jsonschema.validate(self.stac_content, schema)</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.default_validator"><code class="name flex">
    <span>def <span class="ident">default_validator</span></span>(<span>self, stac_type: str) ‑> dict</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Validate the STAC catalog or item against the core schema and its extensions.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>stac_type</code></strong> :&ensp;<code>str</code></dt>
    <dd>The type of STAC object being validated. Must be either "catalog" or "item".</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>A dictionary containing the results of the default validation, including whether the STAC object is valid,
    any validation errors encountered, and any links and assets that were validated.</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def default_validator(self, stac_type: str) -&gt; dict:
        &#34;&#34;&#34;Validate the STAC catalog or item against the core schema and its extensions.

        Args:
            stac_type (str): The type of STAC object being validated. Must be either &#34;catalog&#34; or &#34;item&#34;.

        Returns:
            A dictionary containing the results of the default validation, including whether the STAC object is valid,
            any validation errors encountered, and any links and assets that were validated.
        &#34;&#34;&#34;
        message = self.create_message(stac_type, &#34;default&#34;)
        message[&#34;schema&#34;] = []
        self.core_validator(stac_type)
        core_schema = self.schema
        message[&#34;schema&#34;].append(core_schema)
        stac_type = stac_type.upper()
        if stac_type == &#34;ITEM&#34;:
            message = self.extensions_validator(stac_type)
            message[&#34;validation_method&#34;] = &#34;default&#34;
            message[&#34;schema&#34;].append(core_schema)
        if self.links:
            message[&#34;links_validated&#34;] = self.links_validator()
        if self.assets:
            message[&#34;assets_validated&#34;] = self.assets_validator()
        return message</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.extensions_validator"><code class="name flex">
    <span>def <span class="ident">extensions_validator</span></span>(<span>self, stac_type: str) ‑> dict</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Validate the STAC extensions according to their corresponding JSON schemas.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>stac_type</code></strong> :&ensp;<code>str</code></dt>
    <dd>The STAC object type ("ITEM" or "COLLECTION").</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <dl>
    <dt><code>dict</code></dt>
    <dd>A dictionary containing validation results.</dd>
    </dl>
    <h2 id="raises">Raises</h2>
    <dl>
    <dt><code>JSONSchemaValidationError</code></dt>
    <dd>If there is a validation error in the JSON schema.</dd>
    <dt><code>Exception</code></dt>
    <dd>If there is an error in the STAC extension validation process.</dd>
    </dl></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def extensions_validator(self, stac_type: str) -&gt; dict:
        &#34;&#34;&#34;Validate the STAC extensions according to their corresponding JSON schemas.

        Args:
            stac_type (str): The STAC object type (&#34;ITEM&#34; or &#34;COLLECTION&#34;).

        Returns:
            dict: A dictionary containing validation results.

        Raises:
            JSONSchemaValidationError: If there is a validation error in the JSON schema.
            Exception: If there is an error in the STAC extension validation process.
        &#34;&#34;&#34;
        message = self.create_message(stac_type, &#34;extensions&#34;)
        message[&#34;schema&#34;] = []
        valid = True
        if stac_type == &#34;ITEM&#34;:
            try:
                if &#34;stac_extensions&#34; in self.stac_content:
                    # error with the &#39;proj&#39; extension not being &#39;projection&#39; in older stac
                    if &#34;proj&#34; in self.stac_content[&#34;stac_extensions&#34;]:
                        index = self.stac_content[&#34;stac_extensions&#34;].index(&#34;proj&#34;)
                        self.stac_content[&#34;stac_extensions&#34;][index] = &#34;projection&#34;
                    schemas = self.stac_content[&#34;stac_extensions&#34;]
                    for extension in schemas:
                        if not (is_valid_url(extension) or extension.endswith(&#34;.json&#34;)):
                            # where are the extensions for 1.0.0-beta.2 on cdn.staclint.com?
                            if self.version == &#34;1.0.0-beta.2&#34;:
                                self.stac_content[&#34;stac_version&#34;] = &#34;1.0.0-beta.1&#34;
                                self.version = self.stac_content[&#34;stac_version&#34;]
                            extension = f&#34;https://cdn.staclint.com/v{self.version}/extension/{extension}.json&#34;
                        self.schema = extension
                        self.custom_validator()
                        message[&#34;schema&#34;].append(extension)
            except jsonschema.exceptions.ValidationError as e:
                valid = False
                if e.absolute_path:
                    err_msg = f&#34;{e.message}. Error is in {&#39; -&gt; &#39;.join([str(i) for i in e.absolute_path])}&#34;
                else:
                    err_msg = f&#34;{e.message} of the root of the STAC object&#34;
                message = self.create_err_msg(&#34;JSONSchemaValidationError&#34;, err_msg)
                return message
            except Exception as e:
                valid = False
                err_msg = f&#34;{e}. Error in Extensions.&#34;
                return self.create_err_msg(&#34;Exception&#34;, err_msg)
        else:
            self.core_validator(stac_type)
            message[&#34;schema&#34;] = [self.schema]
        self.valid = valid
        return message</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.links_validator"><code class="name flex">
    <span>def <span class="ident">links_validator</span></span>(<span>self) ‑> dict</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Validate links.</p>
    <h2 id="returns">Returns</h2>
    <p>A dictionary containing the link validation results.</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def links_validator(self) -&gt; dict:
        &#34;&#34;&#34;Validate links.

        Returns:
            A dictionary containing the link validation results.
        &#34;&#34;&#34;
        initial_message = self.create_links_message()
        # get root_url for checking relative links
        root_url = &#34;&#34;
        for link in self.stac_content[&#34;links&#34;]:
            if link[&#34;rel&#34;] in [&#34;self&#34;, &#34;alternate&#34;] and is_valid_url(link[&#34;href&#34;]):
                root_url = (
                    link[&#34;href&#34;].split(&#34;/&#34;)[0] + &#34;//&#34; + link[&#34;href&#34;].split(&#34;/&#34;)[2]
                )
        for link in self.stac_content[&#34;links&#34;]:
            if not is_valid_url(link[&#34;href&#34;]):
                link[&#34;href&#34;] = root_url + link[&#34;href&#34;][1:]
            link_request(link, initial_message)

        return initial_message</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.recursive_validator"><code class="name flex">
    <span>def <span class="ident">recursive_validator</span></span>(<span>self, stac_type: str) ‑> bool</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Recursively validate a STAC JSON document against its JSON Schema.</p>
    <p>This method validates a STAC JSON document recursively against its JSON Schema by following its "child" and "item" links.
    It uses the <code>default_validator</code> and <code>fetch_and_parse_file</code> functions to validate the current STAC document and retrieve the
    next one to be validated, respectively.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>self</code></strong></dt>
    <dd>An instance of the STACValidator class.</dd>
    <dt><strong><code>stac_type</code></strong></dt>
    <dd>A string representing the STAC object type to validate.</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>A boolean indicating whether the validation was successful.</p>
    <h2 id="raises">Raises</h2>
    <dl>
    <dt><code>jsonschema.exceptions.ValidationError</code></dt>
    <dd>If the STAC document does not validate against its JSON Schema.</dd>
    </dl></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def recursive_validator(self, stac_type: str) -&gt; bool:
        &#34;&#34;&#34;Recursively validate a STAC JSON document against its JSON Schema.

        This method validates a STAC JSON document recursively against its JSON Schema by following its &#34;child&#34; and &#34;item&#34; links.
        It uses the `default_validator` and `fetch_and_parse_file` functions to validate the current STAC document and retrieve the
        next one to be validated, respectively.

        Args:
            self: An instance of the STACValidator class.
            stac_type: A string representing the STAC object type to validate.

        Returns:
            A boolean indicating whether the validation was successful.

        Raises:
            jsonschema.exceptions.ValidationError: If the STAC document does not validate against its JSON Schema.

        &#34;&#34;&#34;
        if self.skip_val is False:
            self.schema = set_schema_addr(self.version, stac_type.lower())
            message = self.create_message(stac_type, &#34;recursive&#34;)
            message[&#34;valid_stac&#34;] = False
            try:
                _ = self.default_validator(stac_type)

            except jsonschema.exceptions.ValidationError as e:
                if e.absolute_path:
                    err_msg = f&#34;{e.message}. Error is in {&#39; -&gt; &#39;.join([str(i) for i in e.absolute_path])}&#34;
                else:
                    err_msg = f&#34;{e.message} of the root of the STAC object&#34;
                message.update(
                    self.create_err_msg(&#34;JSONSchemaValidationError&#34;, err_msg)
                )
                self.message.append(message)
                if self.verbose is True:
                    click.echo(json.dumps(message, indent=4))
                return False

            message[&#34;valid_stac&#34;] = True
            self.message.append(message)
            if self.verbose:
                click.echo(json.dumps(message, indent=4))
            self.depth += 1
            if self.max_depth and self.depth &gt;= self.max_depth:
                self.skip_val = True
            base_url = self.stac_file

            for link in self.stac_content[&#34;links&#34;]:
                if link[&#34;rel&#34;] == &#34;child&#34; or link[&#34;rel&#34;] == &#34;item&#34;:
                    address = link[&#34;href&#34;]
                    if not is_valid_url(address):
                        x = str(base_url).split(&#34;/&#34;)
                        x.pop(-1)
                        st = x[0]
                        for i in range(len(x)):
                            if i &gt; 0:
                                st = st + &#34;/&#34; + x[i]
                        self.stac_file = st + &#34;/&#34; + address
                    else:
                        self.stac_file = address
                    self.stac_content = fetch_and_parse_file(str(self.stac_file))
                    self.stac_content[&#34;stac_version&#34;] = self.version
                    stac_type = get_stac_type(self.stac_content).lower()

                if link[&#34;rel&#34;] == &#34;child&#34;:
                    self.recursive_validator(stac_type)

                if link[&#34;rel&#34;] == &#34;item&#34;:
                    self.schema = set_schema_addr(self.version, stac_type.lower())
                    message = self.create_message(stac_type, &#34;recursive&#34;)
                    if self.version == &#34;0.7.0&#34;:
                        schema = fetch_and_parse_schema(self.schema)
                        # this next line prevents this: unknown url type: &#39;geojson.json&#39; ??
                        schema[&#34;allOf&#34;] = [{}]
                        jsonschema.validate(self.stac_content, schema)
                    else:
                        msg = self.default_validator(stac_type)
                        message[&#34;schema&#34;] = msg[&#34;schema&#34;]
                    message[&#34;valid_stac&#34;] = True

                    if self.log != &#34;&#34;:
                        self.message.append(message)
                    if (
                        not self.max_depth or self.max_depth &lt; 5
                    ):  # TODO this should be configurable, correct?
                        self.message.append(message)
        return True</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.run"><code class="name flex">
    <span>def <span class="ident">run</span></span>(<span>self) ‑> bool</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Runs the STAC validation process based on the input parameters.</p>
    <h2 id="returns">Returns</h2>
    <dl>
    <dt><code>bool</code></dt>
    <dd>True if the STAC is valid, False otherwise.</dd>
    </dl>
    <h2 id="raises">Raises</h2>
    <dl>
    <dt><code>URLError</code></dt>
    <dd>If there is an error with the URL.</dd>
    <dt><code>JSONDecodeError</code></dt>
    <dd>If there is an error decoding the JSON content.</dd>
    <dt><code>ValueError</code></dt>
    <dd>If there is an invalid value.</dd>
    <dt><code>TypeError</code></dt>
    <dd>If there is an invalid type.</dd>
    <dt><code>FileNotFoundError</code></dt>
    <dd>If the file is not found.</dd>
    <dt><code>ConnectionError</code></dt>
    <dd>If there is an error with the connection.</dd>
    <dt><code>exceptions.SSLError</code></dt>
    <dd>If there is an SSL error.</dd>
    <dt><code>OSError</code></dt>
    <dd>If there is an error with the operating system.</dd>
    <dt><code>jsonschema.exceptions.ValidationError</code></dt>
    <dd>If the STAC content fails validation.</dd>
    <dt><code>KeyError</code></dt>
    <dd>If the specified key is not found.</dd>
    <dt><code>HTTPError</code></dt>
    <dd>If there is an error with the HTTP connection.</dd>
    <dt><code>Exception</code></dt>
    <dd>If there is any other type of error.</dd>
    </dl></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def run(self) -&gt; bool:
        &#34;&#34;&#34;Runs the STAC validation process based on the input parameters.

        Returns:
            bool: True if the STAC is valid, False otherwise.

        Raises:
            URLError: If there is an error with the URL.
            JSONDecodeError: If there is an error decoding the JSON content.
            ValueError: If there is an invalid value.
            TypeError: If there is an invalid type.
            FileNotFoundError: If the file is not found.
            ConnectionError: If there is an error with the connection.
            exceptions.SSLError: If there is an SSL error.
            OSError: If there is an error with the operating system.
            jsonschema.exceptions.ValidationError: If the STAC content fails validation.
            KeyError: If the specified key is not found.
            HTTPError: If there is an error with the HTTP connection.
            Exception: If there is any other type of error.

        &#34;&#34;&#34;
        message = {}
        try:
            if self.stac_file is not None and not self.item_collection:
                self.stac_content = fetch_and_parse_file(self.stac_file)

            stac_type = get_stac_type(self.stac_content).upper()
            self.version = self.stac_content[&#34;stac_version&#34;]

            if self.core:
                message = self.create_message(stac_type, &#34;core&#34;)
                self.core_validator(stac_type)
                message[&#34;schema&#34;] = [self.schema]
                self.valid = True
            elif self.schema != &#34;&#34;:
                message = self.create_message(stac_type, &#34;custom&#34;)
                message[&#34;schema&#34;] = [self.schema]
                self.custom_validator()
                self.valid = True
            elif self.recursive:
                self.valid = self.recursive_validator(stac_type)
            elif self.extensions:
                message = self.extensions_validator(stac_type)
            else:
                self.valid = True
                message = self.default_validator(stac_type)

        except jsonschema.exceptions.ValidationError as e:
            if e.absolute_path:
                err_msg = f&#34;{e.message}. Error is in {&#39; -&gt; &#39;.join([str(i) for i in e.absolute_path])} &#34;
            else:
                err_msg = f&#34;{e.message} of the root of the STAC object&#34;
            message.update(self.create_err_msg(&#34;JSONSchemaValidationError&#34;, err_msg))

        except (
            URLError,
            JSONDecodeError,
            ValueError,
            TypeError,
            FileNotFoundError,
            ConnectionError,
            exceptions.SSLError,
            OSError,
            KeyError,
            HTTPError,
        ) as e:
            message.update(self.create_err_msg(type(e).__name__, str(e)))

        except Exception as e:
            message.update(self.create_err_msg(&#34;Exception&#34;, str(e)))

        if message:
            message[&#34;valid_stac&#34;] = self.valid
            self.message.append(message)

        if self.log != &#34;&#34;:
            with open(self.log, &#34;w&#34;) as f:
                f.write(json.dumps(self.message, indent=4))

        return self.valid</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.validate_dict"><code class="name flex">
    <span>def <span class="ident">validate_dict</span></span>(<span>self, stac_content) ‑> bool</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Validate the contents of a dictionary representing a STAC object.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>stac_content</code></strong> :&ensp;<code>dict</code></dt>
    <dd>The dictionary representation of the STAC object to validate.</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>A bool indicating if validation was successfull.</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def validate_dict(self, stac_content) -&gt; bool:
        &#34;&#34;&#34;Validate the contents of a dictionary representing a STAC object.

        Args:
            stac_content (dict): The dictionary representation of the STAC object to validate.

        Returns:
            A bool indicating if validation was successfull.
        &#34;&#34;&#34;
        self.stac_content = stac_content
        return self.run()</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.validate_item_collection"><code class="name flex">
    <span>def <span class="ident">validate_item_collection</span></span>(<span>self) ‑> NoneType</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Validate a STAC item collection.</p>
    <h2 id="raises">Raises</h2>
    <dl>
    <dt><code>URLError</code></dt>
    <dd>If there is an issue with the URL used to fetch the item collection.</dd>
    <dt><code>JSONDecodeError</code></dt>
    <dd>If the item collection content cannot be parsed as JSON.</dd>
    <dt><code>ValueError</code></dt>
    <dd>If the item collection does not conform to the STAC specification.</dd>
    <dt><code>TypeError</code></dt>
    <dd>If the item collection content is not a dictionary or JSON object.</dd>
    <dt><code>FileNotFoundError</code></dt>
    <dd>If the item collection file cannot be found.</dd>
    <dt><code>ConnectionError</code></dt>
    <dd>If there is an issue with the internet connection used to fetch the item collection.</dd>
    <dt><code>exceptions.SSLError</code></dt>
    <dd>If there is an issue with the SSL connection used to fetch the item collection.</dd>
    <dt><code>OSError</code></dt>
    <dd>If there is an issue with the file system (e.g., read/write permissions) while trying to write to the log file.</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>None</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def validate_item_collection(self) -&gt; None:
        &#34;&#34;&#34;Validate a STAC item collection.

        Raises:
            URLError: If there is an issue with the URL used to fetch the item collection.
            JSONDecodeError: If the item collection content cannot be parsed as JSON.
            ValueError: If the item collection does not conform to the STAC specification.
            TypeError: If the item collection content is not a dictionary or JSON object.
            FileNotFoundError: If the item collection file cannot be found.
            ConnectionError: If there is an issue with the internet connection used to fetch the item collection.
            exceptions.SSLError: If there is an issue with the SSL connection used to fetch the item collection.
            OSError: If there is an issue with the file system (e.g., read/write permissions) while trying to write to the log file.

        Returns:
            None
        &#34;&#34;&#34;
        page = 1
        print(f&#34;processing page {page}&#34;)
        item_collection = fetch_and_parse_file(str(self.stac_file))
        self.validate_item_collection_dict(item_collection)
        try:
            if self.pages is not None:
                for _ in range(self.pages - 1):
                    if &#34;links&#34; in item_collection:
                        for link in item_collection[&#34;links&#34;]:
                            if link[&#34;rel&#34;] == &#34;next&#34;:
                                page = page + 1
                                print(f&#34;processing page {page}&#34;)
                                next_link = link[&#34;href&#34;]
                                self.stac_file = next_link
                                item_collection = fetch_and_parse_file(
                                    str(self.stac_file)
                                )
                                self.validate_item_collection_dict(item_collection)
                                break
        except Exception as e:
            message = {}
            message[
                &#34;pagination_error&#34;
            ] = f&#34;Validating the item collection failed on page {page}: {str(e)}&#34;
            self.message.append(message)</code></pre>
    </details>
    </dd>
    <dt id="stac_validator.validate.StacValidate.validate_item_collection_dict"><code class="name flex">
    <span>def <span class="ident">validate_item_collection_dict</span></span>(<span>self, item_collection: dict) ‑> NoneType</span>
    </code></dt>
    <dd>
    <div class="desc"><p>Validate the contents of an item collection.</p>
    <h2 id="args">Args</h2>
    <dl>
    <dt><strong><code>item_collection</code></strong> :&ensp;<code>dict</code></dt>
    <dd>The dictionary representation of the item collection to validate.</dd>
    </dl>
    <h2 id="returns">Returns</h2>
    <p>None</p></div>
    <details class="source">
    <summary>
    <span>Expand source code</span>
    </summary>
    <pre><code class="python">def validate_item_collection_dict(self, item_collection: dict) -&gt; None:
        &#34;&#34;&#34;Validate the contents of an item collection.

        Args:
            item_collection (dict): The dictionary representation of the item collection to validate.

        Returns:
            None
        &#34;&#34;&#34;
        for item in item_collection[&#34;features&#34;]:
            self.schema = &#34;&#34;
            self.validate_dict(item)</code></pre>
    </details>
    </dd>
    </dl>
    </dd>
    </dl>
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
    <li><h3><a href="#header-classes">Classes</a></h3>
    <ul>
    <li>
    <h4><code><a title="stac_validator.validate.StacValidate" href="#stac_validator.validate.StacValidate">StacValidate</a></code></h4>
    <ul class="">
    <li><code><a title="stac_validator.validate.StacValidate.assets_validator" href="#stac_validator.validate.StacValidate.assets_validator">assets_validator</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.core_validator" href="#stac_validator.validate.StacValidate.core_validator">core_validator</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.create_err_msg" href="#stac_validator.validate.StacValidate.create_err_msg">create_err_msg</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.create_links_message" href="#stac_validator.validate.StacValidate.create_links_message">create_links_message</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.create_message" href="#stac_validator.validate.StacValidate.create_message">create_message</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.custom_validator" href="#stac_validator.validate.StacValidate.custom_validator">custom_validator</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.default_validator" href="#stac_validator.validate.StacValidate.default_validator">default_validator</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.extensions_validator" href="#stac_validator.validate.StacValidate.extensions_validator">extensions_validator</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.links_validator" href="#stac_validator.validate.StacValidate.links_validator">links_validator</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.recursive_validator" href="#stac_validator.validate.StacValidate.recursive_validator">recursive_validator</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.run" href="#stac_validator.validate.StacValidate.run">run</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.validate_dict" href="#stac_validator.validate.StacValidate.validate_dict">validate_dict</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.validate_item_collection" href="#stac_validator.validate.StacValidate.validate_item_collection">validate_item_collection</a></code></li>
    <li><code><a title="stac_validator.validate.StacValidate.validate_item_collection_dict" href="#stac_validator.validate.StacValidate.validate_item_collection_dict">validate_item_collection_dict</a></code></li>
    </ul>
    </li>
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