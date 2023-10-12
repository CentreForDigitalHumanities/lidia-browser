sql_create_view_annotations = """
CREATE VIEW IF NOT EXISTS view_annotations AS
SELECT
json_extract(content, '$.key') AS id
, json_extract(content, '$.data.parentItem') AS parent_attachment
, json_extract(annotation, '$.argname') AS argname
, json_extract(annotation, '$.arglang') AS arglang
, json_extract(annotation, '$.description') AS description
, json_extract(annotation, '$.argcont') AS argcont
, json_extract(annotation, '$.pagestart') AS page_start
, json_extract(annotation, '$.pageend') AS page_end
, json_extract(annotation, '$.relationType') AS relation_type
, json_extract(annotation, '$.relationTo') AS relation_to
, json_extract(annotation, '$.termgroups') AS termgroups
FROM annotations;
"""

sql_create_view_annotations_termgroups = """
CREATE VIEW IF NOT EXISTS view_annotations_termgroups AS
WITH annotations_termgroups AS (
    SELECT a.id, json_each.value AS termgroup
    FROM annotations a, json_each(a.annotation, '$.termgroups')
)
    SELECT
      id AS annotation_id
    , json_extract(termgroup, '$.termtype') AS termtype
    , json_extract(termgroup, '$.articleterm') AS articleterm
    , CASE
        WHEN json_extract(termgroup, '$.category') != 'custom'
        THEN json_extract(termgroup, '$.category')
        ELSE json_extract(termgroup, '$.customcategory')
      END AS category
    , CASE
        WHEN json_extract(termgroup, '$.lexiconterm') != 'custom'
        THEN json_extract(termgroup, '$.lexiconterm')
        ELSE json_extract(termgroup, '$.customterm')
      END AS lidia_term
FROM annotations_termgroups
ORDER BY id;
"""
