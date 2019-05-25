# Django - CAE Workspace > Documents > javascript_and_react.md

## Description
Instructions for using Javascript/React within the project.

## How Do I know When to Use React Vs Plain JavaScript?
Both are a form of JavaScript. React is just an extension of JavaScript that's meant to make it easier to develop large
pages/apps. Technically, React can be used as a framework to create an entire site, but we want to use Python and
Django, so we only use a subset of what React is capable of.

Generally speaking, plain JavaScript is better for smaller functions, such as handling individual form field widgets,
or making a single CSS class a bit more versatile. In such a case React is generally overkill and not necessary.

React is better for larger ecosystems of interconnected elements, such as if you have a page where clicking/moving one
element may make several other elements dynamically update. In such a case, React will likely help keep the page more
maintainable, long term.

Ultimately, there's not really a hard rule for when to use which, so use what seems to make more sense for the page.

## JavaScript
Any JavaScript code can be added to the project with relatively few steps. The biggest hurdle is just getting it to load
on the appropriate pages.

How the JavaScript is loaded depends on one importat factor: "Does the Script need to run on every single page?"<br>

### Scripts that Occur on Every Page
Scripts embedded into every page are generally universal/core scripts.

Generally speaking, these will be added directly to the `cae_home/templates/cae_home/base.html` template. It should be
added to either the `base_scripts` block or the `base_scripts_body` block.

The only difference between these two is that `base_scripts` will load before most page html (good for libraries and
helper scripts that do no target any specific html elements), while `base_scripts_body` will load after page html (good for
scripts that target specific html elements).

### Scripts that Occur only on Specific Pages
If a script only affects one Django App, or a single page, then it should not be put in the above template file.

Instead, if it's a script loaded on every page of a Django App, load it through
`<your_app>/templates/<your_app>/main.html`. If the script is only meant for a single page, then it should prolly be
loaded on that page's template.

Similarly to above, you should add it to the `extra_scripts` block or the `extra_scripts_body` block.<br>
Just as before, `extra_scripts` will load before moast page html elements, while `extra_scripts_block` will load after
most html elements.

## React
Unfortunately, React uses a syntax that browsers do not intially understand, similarly to SASS. As such, React files
need to be compiled first, before browsers can read it. This is done through NPM.

### Installing NPM
Npm is "the world's largest software registry" and what most front end libraries now seem to install through. It's
required to compile React.

Npm now installs as part of NodeJS. The simplest way to install is to visit:
* https://nodejs.org/

#### Installing Required Npm Packages
Npm will install the required development packages specified in ```packages.json```. This also handles installing the
versions of each package without conflicts.

From the project's root directory, run:
* ```npm install```

#### Updating your Terminal for NPM
(Tip gotten from user hkly at https://dev.to/hkly/running-local-npm-executables-cle )
Now we want to update our local user `.bashrc` file, found at ```~/.bashrc```. This will allow us to run local npm
binaries.

```bash
# Run a local npm binary with 'npm-run COMMAND'
npm-run() {
    $(npm bin)/$*
}
```

Remember to restart your terminal to read the updated `.bashrc` file.

### Compiling react Files through Browserify
#### Compiling Once
This will read the indicated React file, compile the associated JavaScript, and then exit when done.

From the project's root directory, run:
* ```npm-run browserify -t [ babelify --presets [env react] ] <sourceFile> -o <destinationFile>```
    * Where ```\<sourceFile>``` is the original react file.
    * And ```\<destinationFile>``` is where the browser-friendly file is compiled to.

#### Compiling and Watching for Changes
This will read the indicated React file, compile the associated JavaScript, and then continue watching until manually
cancelled. If a new change is detected while watching, it will automatically recompile again.

From the project's root directory, run:
* ```npm-run watchify -v -t [ babelify --presets [env react] ] <sourceFile> -o <destinationFile>```
    * Where ```<sourceFile>``` is the original react file.
    * And ```<destinationFile>``` is where the browser-friendly file is compiled to.
    * The ```-v``` will notify you each time a change is detected.
