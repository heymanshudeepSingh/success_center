# Django - CAE Workspace > Documents > CSS & Templates


## CSS
This project uses custom, in-house SASS code, located in `static/<app_name>/css/`.

This is for 2 main reasons:<br>
1) When this project was started, we made the mistake of thinking "It's just CSS. Surely a markup language can't take
that much extra development time to write.
2) More importantly, we felt like Bootstrap (at the time of creating this project) was overkill, and tended to have too
many complicated, nested classes that you had to remember.

Thus, the CSS for this project was created with "ease of use" in mind.

When creating the CSS, we aimed for minimal classes required in the HTML, while still providing generic and reusable
components.

If serving the site in debug/development mode, then the "CSS Examples" page shows all these reusable elements as they
currently stand. When more generic elements are created, they should also be put into the "CSS Examples" page for
future reference.


## Templates

### Title Tag Template
Page titles should be in format of **\[ Page | App | Site \]**, which seems to be the standard that Google, Stack
Overflow, Django, and other major sites currently go by.

To be as generic as possible, the "Site" part of the title is set to default as "CAE Center". Where appropriate, this
should be overridden with the project name (CAEWeb, West, etc).

### Main Nav and Subnav Menu Format:
Main Header Navigation is in the format of:
```
<li><a href="">Main Item 1</a></li>
<li><a href="">Main Item 2</a></li>
<li>
    <a href="">Main Item 3</a>
    <ul>
        <li><a href="">SubItem Item 1</a></li>
        <li><a href="">SubItem Item 2</a></li>
        <li><a href="">SubItem Item 3</a></li>
    </ul>
</li>
```

### Forms
To make form creation consistent and easy, a reusable form template is provided at
`templates/cae_hom/include/form.html`.

This reusable form template can be used with the command<br>
`{% include 'cae_home/include/form.html' %}`

Note that for the above line to work, the the arguments `form` (for a single form), `forms` (for multiple connected forms), and/or `formset`
(for a many-to-many formset) must be provided on view rendering.

#### Generic Form Template Arguments
The above command to render a form can also take the following arguments:
* **exclude_buttons** - If this argument is provided, then renders the form, minus any buttons.
* **button_text** - Changes the button text from "submit" to the provided argument text.
* **delete_url** - Creates a "Delete" button, with the url linking to the indicated argument text.
* **form_cols** - If this argument is provided, then the form fields will render in column format instead of row format.
