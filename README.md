mupy
====

tiny yaml + jinja static website generator

## Features

mupy simply parses the the data from a yaml file as context for rendering a jinja2 template. Everything is fairly explicit, nothing is magic (well there is \*\*magic). The two bits that are not explicit are processing yaml keys that fit the '\*.md' regex are removed from context, processed via markdown, then put back in with the .md extension dropped. Also, a 'template' key is extracted out of the context and used for processing.
