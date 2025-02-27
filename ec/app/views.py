import datetime
import json
import os
from typing import Optional, Dict
import logging
import cv2
from django.conf import settings
import numpy as np
from PIL import Image, ImageDraw
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
import razorpay
from .models import Customer, Payment, Product, Cart, Wishlist, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from ec.settings import *
from django.db.models import Sum, Count

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@login_required   
def home(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/home.html", locals())

@login_required   
def about(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/about.html",locals())

@login_required   
def contact(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/contact.html",locals())   

@method_decorator(login_required, name='dispatch')
class CategoryView(View):
    def get(self, request, val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        print(product)
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, "app/category.html", locals())
    
@method_decorator(login_required, name='dispatch')
class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, "app/category.html",locals())

@method_decorator(login_required, name='dispatch')
class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user)) if request.user.is_authenticated else None
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, "app/productdetail.html",locals())
    
class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/customerregistration.html', locals())
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User Register Succerfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, 'app/customerregistration.html', locals())
    
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/profile.html', locals())
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request, "Congratulations! Profile Save Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request, 'app/profile.html', locals())
    
def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/address.html',locals())

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request, 'app/updateAddress.html', locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Congratulations! Profile Update Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return redirect("address")
    
@login_required    
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    if not product_id:
        return redirect('/')
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('/cart')

@login_required
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, 'app/addtocart.html', locals())

class checkout(View):
    def get(self,request):
        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        user=request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        razoramount = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {"amount":razoramount,"currency":"INR","receipt":"order_rcptid_11"}
        payment_response = client.order.create(data=data)
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()
        return render(request, 'app/checkout.html', locals())


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount': totalamount
        }
        # print(data)
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

    
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data={
            'amount':amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Wishlist Added Successfully'
            }
        return JsonResponse(data)

def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist.objects.filter(user=user,product=product).delete()
        data={
            'message':'Wishlist Remove Successfully'
            }
        return JsonResponse(data)
    
def search(request):
    query = request.GET['search']
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    product = Product.objects.filter(Q(title__icontains=query))
    return render(request,"app/search.html",locals())

def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    address_id = request.GET.get('address')
    # print("payment_done : oid = ", order_id, " pid = ", payment_id, " aid = ", address_id) 

    user = request.user
    try:
        customer = Customer.objects.get(id=address_id) 
        payment = Payment.objects.get(razorpay_order_id=order_id)

        payment.paid = True
        payment.razorpay_payment_id = payment_id
        payment.save()

        cart = Cart.objects.filter(user=user)
        for c in cart:
            OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity, payment=payment).save()
            c.delete()

        return redirect("orders")

    except Customer.DoesNotExist:
        print(f"Customer with id {address_id} does not exist.")
        return redirect("cart")  

    except Payment.DoesNotExist:
        print(f"Payment with order id {order_id} does not exist.")
        return redirect("cart") 
    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect("cart")

def orders(request):
    order_placed = OrderPlaced.objects.filter(user=request.user)
    # for ord in order_placed:
        # print(ord.product.title, ord.quantity, ord.total_cost)
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/orders.html", locals())


def dashboard(request):
    total_revenue = 0
    daily_revenue = 0
    
    today = datetime.date.today()

    daily_revenue_data = [0] * 7
    daily_order_data = [0] * 7
    
    for order in OrderPlaced.objects.all():
        if order.status == 'Đã giao hàng':
            total_revenue += order.total_cost
            if order.ordered_date.date() == today:
                daily_revenue += order.total_cost

            for i in range(7):
                if order.ordered_date.date() == (today - datetime.timedelta(days=i)):
                    daily_revenue_data[i] += order.total_cost
                    daily_order_data[i] += 1

    category_revenue = OrderPlaced.objects.filter(status='Đã giao hàng').values('product__category').annotate(
        total_revenue=Sum('product__discounted_price') * Sum('quantity')
    )

    state_revenue = OrderPlaced.objects.filter(status='Đã giao hàng').values('customer__state').annotate(
        total_revenue=Sum('product__discounted_price') * Sum('quantity')
    )

    
    daily_revenue_data = daily_revenue_data[::-1]
    daily_order_data = daily_order_data[::-1]
    yesterday_revenue = daily_revenue_data[-2]
    daily_order = daily_order_data[-1]
    yesterday_order = daily_order_data[-2]
    print(daily_order_data)
    context = {
        'total_revenue': total_revenue,
        'daily_revenue': daily_revenue,
        'category_revenue': category_revenue,
        'state_revenue': state_revenue,
        'daily_revenue_data': daily_revenue_data,
        'yesterday_revenue': yesterday_revenue,
        'daily_order': daily_order,
        'yesterday_order': yesterday_order,
    }
    
    return render(request, 'app/dashboard.html', context)



    
def create_directory(directory: str) -> None:
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Đã tạo đường dẫn thành công: {directory}")
    except OSError as e:
        logger.error(f"Lỗi khi tạo đường dẫn {directory}: {e}")
        raise

def get_face_id(directory: str) -> int:
    try:
        if not os.path.exists(directory):
            return 1
            
        user_ids = []
        for filename in os.listdir(directory):
            if filename.startswith('Users-'):
                try:
                    number = int(filename.split('-')[1])
                    user_ids.append(number)
                except (IndexError, ValueError):
                    continue
                    
        return max(user_ids + [0]) + 1
    except Exception as e:
        logger.error(f"Lỗi khi lấy ID khuôn mặt: {e}")
        raise

def save_name(face_id: int, face_name: str, filename: str) -> None:
    try:
        names_json: Dict[str, str] = {}
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as fs:
                    content = fs.read().strip()
                    if content:  
                        names_json = json.loads(content)
            except json.JSONDecodeError:
                logger.warning(f"không thể đọc file {filename}")
                names_json = {}
        
        names_json[str(face_id)] = face_name
        
        with open(filename, 'w') as fs:
            json.dump(names_json, fs, indent=4, ensure_ascii=False)
        logger.info(f"Lưu tên khuôn mặt thành công: {face_id}")
    except Exception as e:
        logger.error(f"Lỗi khi lưu tên khuôn mặt: {e}")
        raise

def initialize_camera(camera_index: int = 0) -> Optional[cv2.VideoCapture]:
    try:
        cam = cv2.VideoCapture(camera_index)
        if not cam.isOpened():
            logger.error("Không thể mở camera")
            return None
            
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA['width'])
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA['height'])
        return cam
    except Exception as e:
        logger.error(f"Lỗi khi khởi tạo camera: {e}")
        return None
    
def get_images_and_labels(path: str):
    try:
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []
    
        detector = cv2.CascadeClassifier(PATHS['cascade_file'])
        if detector.empty():
            raise ValueError("Lỗi khi tải file cascade classifier")

        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')
            
            id = int(os.path.split(imagePath)[-1].split("-")[1])    

            faces = detector.detectMultiScale(img_numpy)

            for (x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y+h, x:x+w])
                ids.append(id)

        return faceSamples, ids
    except Exception as e:
        logger.error(f"Lỗi khi lấy hình ảnh: {e}")
        raise

def face_taker(request):

    if request.method == 'POST':
        try:
            face_name = request.user.username
            customer = get_object_or_404(Customer, user=request.user)
            print(customer.has_face_taker)
            if customer.has_face_taker:
                return JsonResponse({'status': 'error', 'message': 'Bạn đã chụp khuôn mặt'}, status=400)

            customer.has_face_taker = True
            customer.save()


            create_directory(PATHS['image_dir'])
            face_cascade = cv2.CascadeClassifier(PATHS['cascade_file'])
            
            face_id = get_face_id(PATHS['image_dir'])
            save_name(face_id, face_name, PATHS['names_file'])
            
            cam = initialize_camera(CAMERA['index'])
            if cam is None:
                return JsonResponse({'status': 'error', 'message': 'Không thể khởi tạo camera'}, status=500)
            
            count = 0
            while count < TRAINING['samples_needed']:
                ret, img = cam.read()
                if not ret:
                    logger.warning("Không thể đọc khung hình từ camera")
                    continue
                    
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=FACE_DETECTION['scale_factor'],
                    minNeighbors=FACE_DETECTION['min_neighbors'],
                    minSize=FACE_DETECTION['min_size']
                )
                
                for (x, y, w, h) in faces:
                    face_img = gray[y:y+h, x:x+w]
                    img_path = f'./{PATHS["image_dir"]}/Users-{face_id}-{count+1}.jpg'
                    cv2.imwrite(img_path, face_img)
                    count += 1
                    
            cam.release()
            cv2.destroyAllWindows()
            logger.info("Bắt đầu training model...")
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            faces, ids = get_images_and_labels(PATHS['image_dir'])
            
            if not faces or not ids:
                raise ValueError("Không có dữ liệu hình ảnh để train")
                
            logger.info("Training model...")
            recognizer.train(faces, np.array(ids))
            recognizer.write(PATHS['trainer_file'])
            logger.info(f"Model đã được train thành công với {len(np.unique(ids))} mặt")
            
            return render(request, 'app/home.html')
            
        except Exception as e:
            logger.error(f"Lỗi trong quá trình chụp khuôn mặt: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return render(request, 'app/face_taker.html')

@csrf_exempt 
def login_with_face_id(request):
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        if not os.path.exists(PATHS['trainer_file']):
            return JsonResponse({'error': 'Face model not trained yet'}, status=400)
        recognizer.read(PATHS['trainer_file'])

        face_cascade = cv2.CascadeClassifier(PATHS['cascade_file'])
        if face_cascade.empty():
            return JsonResponse({'error': 'Cannot load face cascade classifier'}, status=500)

        cam = cv2.VideoCapture(CAMERA['index'])
        if not cam.isOpened():
            return JsonResponse({'error': 'Cannot initialize camera'}, status=500)

        names = {}
        if os.path.exists(PATHS['names_file']):
            with open(PATHS['names_file'], 'r') as f:
                names = json.load(f)

        ret, img = cam.read()
        if not ret:
            return JsonResponse({'error': 'Cannot capture frame'}, status=500)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=FACE_DETECTION['scale_factor'],
            minNeighbors=FACE_DETECTION['min_neighbors'],
            minSize=FACE_DETECTION['min_size']
        )

        if len(faces) == 0:
            return JsonResponse({'error': 'No face detected'}, status=400)

        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        
        id, confidence = recognizer.predict(face_roi)
        print(confidence)
        if confidence <= 80:
            user_id = str(id)
            if user_id in names:
                username = names[user_id]
                try:
                    user = User.objects.get(username=username)
                    login(request, user)
                    return JsonResponse({
                        'success': True,
                        'message': f'Đăng nhập thành công với username: {username}',
                        'confidence': confidence
                    })
                except User.DoesNotExist:
                    return JsonResponse({'error': 'User not found in database'}, status=404)
            else:
                return JsonResponse({'error': 'Unknown user ID'}, status=400)
        else:
            return JsonResponse({'error': 'Face not recognized'}, status=401)

    except Exception as e:
        logger.error(f"Error during face recognition login: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
    finally:
        if 'cam' in locals():
            cam.release()
        cv2.destroyAllWindows()         
# def login_with_face_id(request):
#     try:
#         recognizer = cv2.face.LBPHFaceRecognizer_create()
#         if not os.path.exists(PATHS['trainer_file']):
#             return JsonResponse({'error': 'Face model not trained yet'}, status=400)
#         recognizer.read(PATHS['trainer_file'])

#         face_cascade = cv2.CascadeClassifier(PATHS['cascade_file'])
#         if face_cascade.empty():
#             return JsonResponse({'error': 'Cannot load face cascade classifier'}, status=500)

#         cam = cv2.VideoCapture(CAMERA['index'])
#         if not cam.isOpened():
#             return JsonResponse({'error': 'Cannot initialize camera'}, status=500)

#         names = {}
#         if os.path.exists(PATHS['names_file']):
#             with open(PATHS['names_file'], 'r') as f:
#                 names = json.load(f)

#         while True:
#             ret, img = cam.read()
#             if not ret:
#                 return JsonResponse({'error': 'Cannot capture frame'}, status=500)

#             gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             faces = face_cascade.detectMultiScale(
#                 gray,
#                 scaleFactor=FACE_DETECTION['scale_factor'],
#                 minNeighbors=FACE_DETECTION['min_neighbors'],
#                 minSize=FACE_DETECTION['min_size']
#             )

#             if len(faces) == 0:
#                 continue  

#             for (x, y, w, h) in faces:
#                 face_roi = gray[y:y+h, x:x+w]
#                 id, confidence = recognizer.predict(face_roi)
#                 print(confidence)
#                 n = 0
#                 if confidence <= 60 & n < 30:
#                     user_id = str(id)
#                     if n >= 30:
#                         return JsonResponse({'error': 'Face not recognized'}, status=400)
#                     if user_id in names:
#                         username = names[user_id]
#                         try:
#                             user = User.objects.get(username=username)
#                             login(request, user)
#                             cam.release()
#                             cv2.destroyAllWindows()
#                             return JsonResponse({
#                                 'success': True,
#                                 'message': f'Successfully logged in as {username}',
#                                 'confidence': confidence
#                             })
#                         except User.DoesNotExist:
#                             cam.release()
#                             cv2.destroyAllWindows()
#                             return JsonResponse({'error': 'User not found in database'}, status=404)
#                     else:
#                         cam.release()
#                         cv2.destroyAllWindows()
#                         return JsonResponse({'error': 'Unknown user ID'}, status=400)
#                 else:
#                     continue  # Face not recognized, continue to next frame

#     except Exception as e:
#         logger.error(f"Error during face recognition login: {e}")
#         return JsonResponse({'error': str(e)}, status=500)
    
#     finally:
#         if 'cam' in locals():
#             cam.release()
#         cv2.destroyAllWindows()

