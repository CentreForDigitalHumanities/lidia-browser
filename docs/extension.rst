
The LIDIA Zotero extension
==========================

.. note::
   This part of the manual is updated for version 0.3.0 of the extension.


Installing the extension
------------------------
The extension consists of the file ``lidia-annotations_v*.*.*.xpi`` and
works together with version 6 of the Zotero desktop application
on all operating systems that Zotero supports (Windows, macOS and Linux).
It is not possible to run the extension using the browser version of Zotero.

After downloading the file, click **Options** → **Add-ons**, click the
option button in the upper-right corner of the window and click
**Install Add-on From File**. After selecting the extension file the
extension will be activated.

.. note::
   The extension should work immediately after activating it. If this is
   not the case, try restarting Zotero.

Activating synchronization with the LIDIA Zotero group
------------------------------------------------------
.. note::
   If you are not able to join the LIDIA group at this moment, it is possible
   to postpone this step and start annotating right away. You can add your
   annotated documents to the group afterwards.

The LIDIA annotations are saved and synchronized in a Zotero group that has
been set up for this purpose. This makes it possible to collaborate with
others on the same documents. Annotated documents inside the group will
automatically become visible on the LIDIA website (or at least, that is the
plan!).

The Zotero group is a private group and you should request an invitation
to join it. Once you receive the invitation, you can join the group using
the link you receive by e-mail.

To contribute to the group, it is necessary to enable synchronization with your
Zotero account. For this, click **Edit** → **Preferences** and enter your
username and password. If necessary, there is a link to create an account.
After joining the group and enabling synchronization, the group will be
visible in Zotero as a folder and any document and attached file you add
to this folder will be part of the group library.

Annotating a document
---------------------
To start annotating, first make sure that you have a bibliographical
Zotero item (e.g. a book, a chapter of a book or an article in a journal)
with an attached PDF file. You can create the bibliographical item in the
usual way using the various options that Zotero supports. You can upload
the PDF then from your own computer by right-clicking and selecting
**Add attachment** → **Add copy of file**.
At this stage, you can choose whether you
want to work with the document inside your own library or in the shared
LIDIA library, because you can move items including your annotations around
without problems.

.. note::
   Zotero allows you to work with a link to a local PDF file as an alternative
   to importing the PDF to your Zotero library. This will work, but it will
   not be possible to add the file with its annotation to a shared group
   in this case. Working with links to online PDF files is not possible because
   these will always be opened externally.

Next, open the PDF file by double-clicking it. The PDF will open inside
the Zotero window. You will then need to open the two sidebars on the left
and right hands of the window by clicking the leftmost button and the button
second from the right on the toolbar.

You can create an annotation by selecting a piece of text and selecting a
colour to mark the text with. The colour you choose is ignored by LIDIA.
The annotation will immediately be visible in the overview of annotations
in the sidebar on the left. Click the new annotation, and in the sidebar
on the right you will see editable fields in the LIDIA toolbar. You can
now fill in the fields and click **Save** to save your annotation. If you
have activated synchronization with your Zotero account, your annotation
will immediately be saved online in your account as well. If you have put
the document in the LIDIA Zotero group, it will also be visible for other
users of the group.

Editing annotations
-------------------
Editing annotations works the same as creating new ones: click the annotation
in the sidebar on the left and start editing.

If the annotation was created by another user in the same group, you can
view the annotation but you cannot edit it.

You can only edit annotations that are new (i.e., they do not contain
a comment) or that were saved by the LIDIA extension. Existing annotations
can be converted to LIDIA extensions, however.

.. note::
   It is not possible to edit annotations by selecting the annotations
   from within the text -- you have to use the sidebar on the left.

Annotations that run on multiple pages
--------------------------------------
Zotero does not allow annotations that run over the borders of a single page.
It is possible to annotate text that covers multiple pages, but Zotero will
create multiple annotations for it automatically. To annotate an argument that
runs over multiple pages, do the following:

* Create an annotation for all of the text. Zotero will automatically split
  this up into one annotation per page.
* Select the first created annotation (on the first page of the text), fill
  out the LIDIA form, and save the annotation
* Select the annotations on the subsequent pages one by one, select the
  checkbox **Annotation is continuation of previous argument**, and save. You
  will see that the rest of the form will be greyed out and that the information
  that you just have filled in is shown.

LIDIA does not support annotations that run across multiple non-continious
annotations. Instead, you may use the **Relation** field to indicate that
there are multiple annotations for one linguistic argument.

Relations between annotations
-----------------------------
Use the **Relation** field to indicate that an annotation is somehow
related to a different annotation. The first box defines the
type of the relation, such as *Contradicts* and *Generalizes*. In the
second box you indicate to which annotation it is related. You can select from
all LIDIA annotations from the same Zotero library as that of the document
that you are currently working in. The references to the annotations
are shown using the title of the document and the name of the argument,
separated by a colon (:).

Setting default values
----------------------
It is possible to set default values for certain fields that are likely
to remain the same throughout a document. To do that, go to the library tab
(the leftmost tab), select the parent bibliographical item of the PDF file,
and go to the **Extra** field at the right side of the screen inside the
**Info** tab. This field is normally empty, but you can add LIDIA defaults to
it, such as:

::

  lidia.default_arglang: eng
  lidia.default_termcategory: morphosyntax

This will set the default argument language to English, and the default
lexicon term category to General. For ``lidia.default_arglang``, choose the
right ISO 639-3 language code (codes consisting of three characters, such as
``nld`` for Dutch). For ``lidia.default_termcategory``, choose from the
lexicon term categories that you find in the LIDIA form in the first combo box
of the **Lexicon term** field, but in lowercase and with spaces replaced by
dashes (such as ``part-of-speech``).

Working with existing PDF annotations
-------------------------------------
PDF readers, such as Adobe Acrobat Reader, have their own annotation
capabilities. These annotations are saved as part of the PDF files.
Zotero, however, works with a different format for annotations where they
are not part of the PDF file but instead part of your Zotero library.
The advantage is that they can easily be shared with other people in
your Zotero group without uploading the full PDF time every time you make
a change.

Zotero is capable of working with existing PDF annotations. To work with them
in LIDIA, however, you first have to convert them to Zotero annotations.
After importing the PDF in Zotero, open the PDF in the built-in reader
and click **File** → **Import Annotations**. Zotero will warn you that the
annotations will be removed from the PDF file and imported to your Zotero
library. That is because you would otherwise see a double set of annotations.
If you are working with local files, make sure you have a backup in case
of a failure during the import of the annotations.

.. note::
   Apparently it is not possible to import PDF annotations in files that are
   part of a shared Zotero group. If this is the case, first move the file
   to your personal Zotero library, import the annotations and move the file
   back to the group.

Imported annotations will not be in the LIDIA format. You can convert them
by clicking an annotation and clicking the **Convert to LIDIA annotation**
button in the sidebar on the right side of the screen. LIDIA will then attempt
to read the existing annotation as a LIDIA annotation, with the text on the
first line as the annotation ID and the rest of the text as the description
of the argument.
