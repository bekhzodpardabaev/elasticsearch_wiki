# [ElasticSearch](#https://www.elastic.co/) 


### 1. `pip install django-elasticsearch-dsl-drf`
### 2. `django_elasticsearch_dsl_drf` va `django_elasticsearch_dsl` kutubxonalarni `INSTALLED_APPS` ga qo’shish.
### 3. settings ga `ELASTICSEARCH_DSL` ni o'rnatish. Namuna
```
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://localhost:9200'
    },
}
```
### 4. Model. Namuna
```
    class Book(models.Model):
        title = models.CharField(max_length=100)
        description = models.TextField(null=True, blank=True)
        summary = models.TextField(null=True, blank=True)
        authors = models.ManyToManyField('books.Author', related_name='books')
        publisher = models.ForeignKey(Publisher, related_name='books', on_delete=models.CASCADE)
        publication_date = models.DateField()
        state = models.CharField(max_length=100)
        isbn = models.CharField(max_length=100, unique=True)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        pages = models.PositiveIntegerField(default=200)
        stock_count = models.PositiveIntegerField(default=30)
        tags = models.ManyToManyField('books.Tag',
                                    related_name='books',
                                    blank=True)

        class Meta:
            ordering = ["isbn"]

        def __str__(self):
            return self.title
        @property
        def tags_indexing(self):
            return [tag.title for tag in self.tags.all()]

```
### 5. `Book` model uchun Document
### Document - Model'ni ES ga indexlash uchun kerak
```
class BookDocument(Document):
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
        model = Book
```
### 6. DocumentSerializer bu DRF dagi serializer kabi ishlaydi, farqi DRF serializer model serializatsiya qilsa, DocumentSerializer Document'ni serializatsiya qiladi.
```
class BookDocumentSerializer(DocumentSerializer):

    class Meta:
        document = BookDocument

        fields = (
            'id',
            'title',
            'description',
            'summary',
            'publisher',
            'publication_date',
            'state',
            'isbn',
            'price',
            'pages',
            'stock_count',
            'tags',
        )
```
### 7. ViewSet
```
class BookDocumentView(BaseDocumentViewSet):
    document = BookDocument
    serializer_class = BookDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        SearchFilterBackend,
    ]
    search_fields = (
        'title',
        'description',
        'summary',
    )
    filter_fields = {
        'id': {
            'field': 'id',
            # Note, that we limit the lookups of id field in this example,
            # to `range`, `in`, `gt`, `gte`, `lt` and `lte` filters.
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'title': 'title',

        'pages': {
            'field': 'pages',
            # Note, that we limit the lookups of `pages` field in this
            # example, to `range`, `gt`, `gte`, `lt` and `lte` filters.
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'stock_count': {
            'field': 'stock_count',
            # Note, that we limit the lookups of `stock_count` field in
            # this example, to `range`, `gt`, `gte`, `lt` and `lte`
            # filters.
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'tags': {
            'field': 'tags',
            # Note, that we limit the lookups of `tags` field in
            # this example, to `terms, `prefix`, `wildcard`, `in` and
            # `exclude` filters.
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },
    }
```
### 8. Url ga qo'shish
```
router = DefaultRouter()
books = router.register(r'books', BookDocumentView, basename='bookdocument')


urlpatterns = [
    path('es/book/', include(router.urls)),
]
```
### 9. Qo'shimcha filter backend'lar
1. `FilteringFilterBackend` - bu har field uchun individual filter qoyish, yani agar field IntegerField unga lt, gt, lte, gte, range, in kabi filterlar qilish mumkin. Har bir field uchun alohida qilinadi! Boshqa field turlari uchun https://django-elasticsearch-dsl-drf.readthedocs.io doc dan o'qib olish mumkin. Namuna: 
    ```
    filter_backends = [
        FilteringFilterBackend
    ]
    filter_fields = {
        'id': {
            'field': 'id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
    ```
    Ishlatish: 
    ```
    some_path/?id__lte=4
    some_path/?id__range=10__20
    ```
2. `SearchFilterBackend` - Bir nechta field'lar qidirish. Namuna: 
    ```
    filter_backends = [
        SearchFilterBackend
    ]
    search_fields = (
        'title',
        'description',
        'summary',
    )
    ```
    Ishlatish: 
    ```
    some_path/?search=Lorem
    ```
3. `MultiMatchSearchFilterBackend` - bu `SearchFilterBackend` kabi ishlaydi, farqi `MultiMatchSearchFilterBackend` da searchda fieldlarga vazn bersa bo'ladi.
   Manuma:
   ```
    filter_backends = [
        MultiMatchSearchFilterBackend
    ]
    multi_match_search_fields = {
        "title": {"boost": 7},
        "description": {"boost": 3},
    }
    ```
    Ishlatish: 
    ```
    some_path/?multi_match_search=Lorem
    ```
4. `SuggesterFilterBackend` - bu suggest uchun.
5. `IdsFilterBackend` - Id bilan filterlash.
   Manuma:
   ```
    filter_backends = [
        IdsFilterBackend
    ]
    ```
    Ishlatish: 
    ```
    some_path/?ids=1__2__3 yoki some_path/?ids=1&ids=2&ids=3
    ```
