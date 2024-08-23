from django.db import models

class ProductDetails(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    subcategory = models.CharField(max_length=255, null=True, blank=True)
    product = models.CharField(max_length=255, null=True, blank=True)
    product_like = models.IntegerField(null=True, blank=True)
    product_price = models.IntegerField(null=True, blank=True)
    price_range = models.CharField(max_length=255, blank=True)
    product_tag = models.CharField(max_length=255, null=True, blank=True)
    cumulative_sales_volume = models.CharField(max_length=255, null=True, blank=True)
    purchases = models.IntegerField(null=True, blank=True)
    purchases_18 = models.IntegerField(null=True, blank=True)
    purchases_19_23 = models.IntegerField(null=True, blank=True)
    purchases_24_28 = models.IntegerField(null=True, blank=True)
    purchases_29_33 = models.IntegerField(null=True, blank=True)
    purchases_34_39 = models.IntegerField(null=True, blank=True)
    purchases_40 = models.IntegerField(null=True, blank=True)
    purchases_male = models.IntegerField(null=True, blank=True)
    purchases_female = models.IntegerField(null=True, blank=True)
    views = models.IntegerField(null=True, blank=True)
    views_18 = models.IntegerField(null=True, blank=True)
    views_19_23 = models.IntegerField(null=True, blank=True)
    views_24_28 = models.IntegerField(null=True, blank=True)
    views_29_33 = models.IntegerField(null=True, blank=True)
    views_34_39 = models.IntegerField(null=True, blank=True)
    views_40 = models.IntegerField(null=True, blank=True)
    views_male = models.IntegerField(null=True, blank=True)
    views_female = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.product} - {self.id}"


class ProductReview(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    product_id = models.ForeignKey(ProductDetails, on_delete=models.CASCADE, to_field="id", db_column="product_id")  # 외래 키로 설정
    review = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    sex = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    helpful = models.IntegerField(null=True, blank=True)
    style_like = models.IntegerField(null=True, blank=True)
    reviewtag_size = models.CharField(max_length=255, null=True, blank=True)
    reviewtag_brightness = models.CharField(max_length=255, null=True, blank=True)
    reviewtag_color = models.CharField(max_length=255, null=True, blank=True)
    reviewtag_thickness = models.CharField(max_length=255, null=True, blank=True)
    reviewtag_warmth = models.CharField(max_length=255, null=True, blank=True)
    reviewtag_weight = models.CharField(max_length=255, null=True, blank=True)
    reviewtag_delivery = models.CharField(max_length=255, null=True, blank=True)
    reviewtag_packaging = models.CharField(max_length=255, null=True, blank=True)
    review_tokens = models.TextField(null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)
    emotions = models.CharField(max_length=50, null =True, blank=True)

    def __str__(self):
        return f"{self.product_ID.product} - {self.review_ID}"
    
    