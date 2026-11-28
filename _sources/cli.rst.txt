CLI API Reference
=================

.. raw:: html

    <embed>
        <!doctype html>
        <html lang="en">
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1" />
        <meta name="generator" content="pdoc 0.9.2" />
        <title>stac_validator.stac_validator API documentation</title>
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
        <h1 class="title">Module <code>stac_validator.stac_validator</code></h1>
        </header>
        <section id="section-intro">
        <details class="source">
        <summary>
        <span>Expand source code</span>
        </summary>
        <pre><code class="python">import json
        import sys
        from typing import Any, Dict, List

        import click  # type: ignore
        import pkg_resources

        from .validate import StacValidate


        def print_update_message(version: str) -&gt; None:
            &#34;&#34;&#34;Prints an update message for `stac-validator` based on the version of the
            STAC file being validated.

            Args:
                version (str): The version of the STAC file being validated.

            Returns:
                None
            &#34;&#34;&#34;
            click.secho()
            if version != &#34;1.0.0&#34;:
                click.secho(
                    f&#34;Please upgrade from version {version} to version 1.0.0!&#34;, fg=&#34;red&#34;
                )
            else:
                click.secho(&#34;Thanks for using STAC version 1.0.0!&#34;, fg=&#34;green&#34;)
            click.secho()


        def item_collection_summary(message: List[Dict[str, Any]]) -&gt; None:
            &#34;&#34;&#34;Prints a summary of the validation results for an item collection response.

            Args:
                message (List[Dict[str, Any]]): The validation results for the item collection.

            Returns:
                None
            &#34;&#34;&#34;
            valid_count = 0
            for item in message:
                if &#34;valid_stac&#34; in item and item[&#34;valid_stac&#34;] is True:
                    valid_count = valid_count + 1
            click.secho()
            click.secho(&#34;--item-collection summary&#34;, bold=True)
            click.secho(f&#34;items_validated: {len(message)}&#34;)
            click.secho(f&#34;valid_items: {valid_count}&#34;)


        @click.command()
        @click.argument(&#34;stac_file&#34;)
        @click.option(
            &#34;--core&#34;, is_flag=True, help=&#34;Validate core stac object only without extensions.&#34;
        )
        @click.option(&#34;--extensions&#34;, is_flag=True, help=&#34;Validate extensions only.&#34;)
        @click.option(
            &#34;--links&#34;,
            is_flag=True,
            help=&#34;Additionally validate links. Only works with default mode.&#34;,
        )
        @click.option(
            &#34;--assets&#34;,
            is_flag=True,
            help=&#34;Additionally validate assets. Only works with default mode.&#34;,
        )
        @click.option(
            &#34;--custom&#34;,
            &#34;-c&#34;,
            default=&#34;&#34;,
            help=&#34;Validate against a custom schema (local filepath or remote schema).&#34;,
        )
        @click.option(
            &#34;--recursive&#34;,
            &#34;-r&#34;,
            is_flag=True,
            help=&#34;Recursively validate all related stac objects.&#34;,
        )
        @click.option(
            &#34;--max-depth&#34;,
            &#34;-m&#34;,
            type=int,
            help=&#34;Maximum depth to traverse when recursing. Omit this argument to get full recursion. Ignored if `recursive == False`.&#34;,
        )
        @click.option(
            &#34;--item-collection&#34;,
            is_flag=True,
            help=&#34;Validate item collection response. Can be combined with --pages. Defaults to one page.&#34;,
        )
        @click.option(
            &#34;--pages&#34;,
            &#34;-p&#34;,
            type=int,
            help=&#34;Maximum number of pages to validate via --item-collection. Defaults to one page.&#34;,
        )
        @click.option(
            &#34;-v&#34;, &#34;--verbose&#34;, is_flag=True, help=&#34;Enables verbose output for recursive mode.&#34;
        )
        @click.option(&#34;--no_output&#34;, is_flag=True, help=&#34;Do not print output to console.&#34;)
        @click.option(
            &#34;--log_file&#34;,
            default=&#34;&#34;,
            help=&#34;Save full recursive output to log file (local filepath).&#34;,
        )
        @click.version_option(version=pkg_resources.require(&#34;stac-validator&#34;)[0].version)
        def main(
            stac_file: str,
            item_collection: bool,
            pages: int,
            recursive: bool,
            max_depth: int,
            core: bool,
            extensions: bool,
            links: bool,
            assets: bool,
            custom: str,
            verbose: bool,
            no_output: bool,
            log_file: str,
        ) -&gt; None:
            &#34;&#34;&#34;Main function for the `stac-validator` command line tool. Validates a STAC file
            against the STAC specification and prints the validation results to the console as JSON.

            Args:
                stac_file (str): Path to the STAC file to be validated.
                item_collection (bool): Whether to validate item collection responses.
                pages (int): Maximum number of pages to validate via `item_collection`.
                recursive (bool): Whether to recursively validate all related STAC objects.
                max_depth (int): Maximum depth to traverse when recursing.
                core (bool): Whether to validate core STAC objects only.
                extensions (bool): Whether to validate extensions only.
                links (bool): Whether to additionally validate links. Only works with default mode.
                assets (bool): Whether to additionally validate assets. Only works with default mode.
                custom (str): Path to a custom schema file to validate against.
                verbose (bool): Whether to enable verbose output for recursive mode.
                no_output (bool): Whether to print output to console.
                log_file (str): Path to a log file to save full recursive output.

            Returns:
                None

            Raises:
                SystemExit: Exits the program with a status code of 0 if the STAC file is valid,
                    or 1 if it is invalid.
            &#34;&#34;&#34;
            valid = True
            stac = StacValidate(
                stac_file=stac_file,
                item_collection=item_collection,
                pages=pages,
                recursive=recursive,
                max_depth=max_depth,
                core=core,
                links=links,
                assets=assets,
                extensions=extensions,
                custom=custom,
                verbose=verbose,
                log=log_file,
            )
            if not item_collection:
                valid = stac.run()
            else:
                stac.validate_item_collection()

            message = stac.message
            if &#34;version&#34; in message[0]:
                print_update_message(message[0][&#34;version&#34;])

            if no_output is False:
                click.echo(json.dumps(message, indent=4))

            if item_collection:
                item_collection_summary(message)

            sys.exit(0 if valid else 1)


        if __name__ == &#34;__main__&#34;:
            main()</code></pre>
        </details>
        </section>
        <section>
        </section>
        <section>
        </section>
        <section>
        <h2 class="section-title" id="header-functions">Functions</h2>
        <dl>
        <dt id="stac_validator.stac_validator.item_collection_summary"><code class="name flex">
        <span>def <span class="ident">item_collection_summary</span></span>(<span>message: List[Dict[str, Any]]) ‑> NoneType</span>
        </code></dt>
        <dd>
        <div class="desc"><p>Prints a summary of the validation results for an item collection response.</p>
        <h2 id="args">Args</h2>
        <dl>
        <dt><strong><code>message</code></strong> :&ensp;<code>List[Dict[str, Any]]</code></dt>
        <dd>The validation results for the item collection.</dd>
        </dl>
        <h2 id="returns">Returns</h2>
        <p>None</p></div>
        <details class="source">
        <summary>
        <span>Expand source code</span>
        </summary>
        <pre><code class="python">def item_collection_summary(message: List[Dict[str, Any]]) -&gt; None:
            &#34;&#34;&#34;Prints a summary of the validation results for an item collection response.

            Args:
                message (List[Dict[str, Any]]): The validation results for the item collection.

            Returns:
                None
            &#34;&#34;&#34;
            valid_count = 0
            for item in message:
                if &#34;valid_stac&#34; in item and item[&#34;valid_stac&#34;] is True:
                    valid_count = valid_count + 1
            click.secho()
            click.secho(&#34;--item-collection summary&#34;, bold=True)
            click.secho(f&#34;items_validated: {len(message)}&#34;)
            click.secho(f&#34;valid_items: {valid_count}&#34;)</code></pre>
        </details>
        </dd>
        <dt id="stac_validator.stac_validator.print_update_message"><code class="name flex">
        <span>def <span class="ident">print_update_message</span></span>(<span>version: str) ‑> NoneType</span>
        </code></dt>
        <dd>
        <div class="desc"><p>Prints an update message for <code>stac-validator</code> based on the version of the
        STAC file being validated.</p>
        <h2 id="args">Args</h2>
        <dl>
        <dt><strong><code>version</code></strong> :&ensp;<code>str</code></dt>
        <dd>The version of the STAC file being validated.</dd>
        </dl>
        <h2 id="returns">Returns</h2>
        <p>None</p></div>
        <details class="source">
        <summary>
        <span>Expand source code</span>
        </summary>
        <pre><code class="python">def print_update_message(version: str) -&gt; None:
            &#34;&#34;&#34;Prints an update message for `stac-validator` based on the version of the
            STAC file being validated.

            Args:
                version (str): The version of the STAC file being validated.

            Returns:
                None
            &#34;&#34;&#34;
            click.secho()
            if version != &#34;1.0.0&#34;:
                click.secho(
                    f&#34;Please upgrade from version {version} to version 1.0.0!&#34;, fg=&#34;red&#34;
                )
            else:
                click.secho(&#34;Thanks for using STAC version 1.0.0!&#34;, fg=&#34;green&#34;)
            click.secho()</code></pre>
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
        <li><code><a title="stac_validator.stac_validator.item_collection_summary" href="#stac_validator.stac_validator.item_collection_summary">item_collection_summary</a></code></li>
        <li><code><a title="stac_validator.stac_validator.print_update_message" href="#stac_validator.stac_validator.print_update_message">print_update_message</a></code></li>
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