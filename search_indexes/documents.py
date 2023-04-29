# Name of the Elasticsearch index
from django.conf import settings
from django_elasticsearch_dsl import Index, Document, fields
from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl_drf.analyzers import edge_ngram_completion
from books.models import Book
from django_elasticsearch_dsl_drf.compat import KeywordField, StringField
INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES['books'])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)

html_strip = None

html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)


@INDEX.doc_type
class BookDocument(Document):
    """Book Elasticsearch document."""

    id = fields.IntegerField()

    title = fields.TextField(analyzer=html_strip,
        fields={
            "raw": KeywordField(),
            "suggest": fields.CompletionField(),
            "edge_ngram_completion": StringField(
                analyzer=edge_ngram_completion
            ),
        }
    )

    description = fields.TextField()

    summary = fields.TextField()

    # publisher = fields.TextField()

    publication_date = fields.DateField()

    state = fields.TextField()

    isbn = fields.TextField()

    price = fields.FloatField()

    pages = fields.IntegerField()

    stock_count = fields.IntegerField()

    tags = fields.TextField(
        attr='tags_indexing',
        fields={
            'raw': fields.TextField(multi=True),
            'suggest': fields.TextField(multi=True),
        },
        multi=True
    )

    class Django(object):
        """Inner nested class Django."""

        model = Book  # The model associate with this Document
