from django.db import models
from django.contrib.auth.models import User

# Create your models here.
STATE_CHOICES = (
    ('AG', 'An Giang'),
    ('BV', 'Bà Rịa - Vũng Tàu'),
    ('BL', 'Bạc Liêu'),
    ('BK', 'Bắc Kạn'),
    ('BG', 'Bắc Giang'),
    ('BN', 'Bắc Ninh'),
    ('BT', 'Bến Tre'),
    ('BD', 'Bình Định'),
    ('BP', 'Bình Phước'),
    ('BH', 'Bình Thuận'),
    ('CM', 'Cà Mau'),
    ('CB', 'Cao Bằng'),
    ('CT', 'Cần Thơ'),
    ('DN', 'Đà Nẵng'),
    ('DL', 'Đắk Lắk'),
    ('ĐN', 'Đắk Nông'),
    ('DB', 'Điện Biên'),
    ('ĐG', 'Đồng Nai'),
    ('ĐT', 'Đồng Tháp'),
    ('GL', 'Gia Lai'),
    ('HG', 'Hà Giang'),
    ('HN', 'Hà Nội'),
    ('HT', 'Hà Tĩnh'),
    ('HD', 'Hải Dương'),
    ('HP', 'Hải Phòng'),
    ('HM', 'Hậu Giang'),
    ('HB', 'Hòa Bình'),
    ('HY', 'Hưng Yên'),
    ('KH', 'Khánh Hòa'),
    ('KG', 'Kiên Giang'),
    ('KT', 'Kon Tum'),
    ('LC', 'Lai Châu'),
    ('LD', 'Lâm Đồng'),
    ('LS', 'Lạng Sơn'),
    ('LĐ', 'Lào Cai'),
    ('LA', 'Long An'),
    ('ND', 'Nam Định'),
    ('NA', 'Nghệ An'),
    ('NB', 'Ninh Bình'),
    ('NT', 'Ninh Thuận'),
    ('PT', 'Phú Thọ'),
    ('PY', 'Phú Yên'),
    ('QB', 'Quảng Bình'),
    ('QA', 'Quảng Nam'),
    ('QG', 'Quảng Ngãi'),
    ('QN', 'Quảng Ninh'),
    ('QT', 'Quảng Trị'),
    ('ST', 'Sóc Trăng'),
    ('SL', 'Sơn La'),
    ('TH', 'Tây Ninh'),
    ('TB', 'Thái Bình'),
    ('TN', 'Thái Nguyên'),
    ('TH', 'Thanh Hóa'),
    ('TT', 'Thừa Thiên - Huế'),
    ('TG', 'Tiền Giang'),
    ('TV', 'Trà Vinh'),
    ('TQ', 'Tuyên Quang'),
    ('VL', 'Vĩnh Long'),
    ('VP', 'Vĩnh Phúc'),
    ('YB', 'Yên Bái'),
)


CATEGORY_CHOICES=(
    ('Thoi_trang_nam', 'Thời trang nam'),
    ('Thoi_trang_nu', 'Thời trang nữ'),
    ('Dien_thoai', 'Điện thoại & phụ kiện'),
    ('Me_va_be', 'Mẹ & bé'),
    ('Thiet_bi_dien_tu', 'Thiết bị điện tử'),
    ('Nha_cua_doi_song', 'Nhà cửa & đời sống'),
    ('May_tinh_laptop', 'Máy tính & laptop'),
    ('Sac_dep', 'Sắc đẹp')
)

STATUS_CHOICES = (
    ('Chờ xác nhận', 'Chờ xác nhận'), 
    ('Đã chấp nhận', 'Đã chấp nhận'), 
    ('Đang Đóng gói', 'Đang Đóng gói'),      
    ('Đang giao hàng', 'Đang giao hàng'), 
    ('Đã giao hàng', 'Đã giao hàng'),  
    ('Hủy đơn', 'Hủy đơn'),    
)

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    desciption = models.TextField()
    composition = models.TextField(default='')
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    product_image = models.ImageField(upload_to='product')
    def __str__(self):
        return self.title
    
class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.IntegerField(default=0)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=100)
    has_face_taker = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_status = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    paid = models.BooleanField(default=False)
    
class OrderPlaced(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Chờ xác nhận')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, default="")
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
