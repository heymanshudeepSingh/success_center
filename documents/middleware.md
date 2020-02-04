# Django - CAE Workspace > Documents > middleware.md

## Description
Middleware is essentially "any logic that automatically runs on every single page load". It can be found at
`<app_name>/middleware.py`.

For full details on general middleware logic for Django, see
<https://docs.djangoproject.com/en/dev/topics/http/middleware/>.

As far as this project goes, most middleware is likely to be under `cae_home/middleware.py`.

## CAE Home Middleware
The following is custom logic currently established by middleware in `cae_home/middleware.py`.

### View Logic
The following values affect all view logic.

#### User Profile Access
When logged in, the User's `Profile` model is accessible via `request.user.profile`.

#### User Timezone Setting
Each User's `Profile` model has a `timezone` field. When logged in, middleware should grab this value and adjust all
datetime values on the page accordingly.

### Templating Variables
The following variables are available in all templates, as long as it's served by the view with a `TemplateResponse`.

#### Project Domain
The project domain url is accessible with `{{ domain }}`.

This will display the full domain of the site, without any page url information. This is useful such as when creating
websockets in JavaScript.

For example, when serving in standard development mode, this should provide `127.0.0.1:8000` as the domain.

#### Imported Project List
The list of all currently installed and active projects is provided as `{{ imported_projects }}`.

To elaborate, this is the list of all projects that are both:
1) Whitelisted under `settings/allowed_apps.py`
2) Currently included under the `apps` folder.

Ex: CAE_Web, CICO, etc.

#### CAE Center Contact Info
Currently, only the CAE Programmer email is automatically provided to all pages, accessible via `{{ cae_prog_email }}`.

#### User Profile Settings
While the entire user's `Profile` model is provided directly to views (see above), only a portion of `Profile` model
values are provided to all templates. They are as follows:
* `{{ site_theme }}` - The user's currently selected CSS theme. Defaults to `wmu` when not logged in.
* `{{ desktop_font_size }}` - The user's currently selected desktop font size. Defaults to `base`.
* `{{ mobile_font_size }}` - The user's currently selected mobile font size. Defaults to `base`.

#### Main Nav Templating Path
This one is a bit special. It can be accessed via `{{ main_nav_template_path }}`.

Essentially, there was an issue when navigating to `cae_home` pages (such as the user profile edit page) from any
project. For example, if navigating to a `cae_home` page from `CAE_Web`, the main nav at the top of the page would
change.

CAE Home only has minimal (most development/testing) main nav, so users would get stuck, unable to go back to the
project they originally were on.

This main nav middleware is an attempt to fix that. Basically, it does the following:
1) On page load, attempt to read in the current page url. This url is split apart, and the middleware grabs the current
project name (cae_web, cico, etc).
2) Using this project name value, the middleware attempts to find a match from the currently active `allowed_apps.py`
logic.
3) If a match is found, then the path to this project's main nav template file is saved as a template variable
(Ex: `cae_web_core/app_nav.html`).
4) Note that CAE Home urls are not included in this, so any pages from CAE Home will not override previously saved
template locations.
5) Next, the page is rendered. This previously saved template variable is accessed, providing the "proper" nav template
to display.
6) In instances when no template variable is provided (such as when CAE Home pages have been accessed, but not other
projects), then the CAE Home nav template is provided as a default.

Ultimately, this should make it so that if a user accesses a project, and then a CAE Home view afterwards, the main nav
should still display urls for the most recently accessed project.
