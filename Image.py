import cv2, code
from PIL import Image
import numpy as np
from scipy.spatial import distance
import matplotlib.pyplot as plt

def max_entropy_imageJ(data):
    total = data.sum()
    #code.interact(local=dict(globals(), **locals()))

    norm_histo = data / total

    P1 = np.zeros(len(norm_histo))
    P2 = np.zeros(len(norm_histo))
    #P1 = np.copy(norm_histo)\
    P1[0]=norm_histo[0];
    P2[0]=1.0-P1[0];

    for ih in range(len(norm_histo)):
        P1[ih]= P1[ih-1] + norm_histo[ih];
        P2[ih]= 1.0 - P1[ih];


    valid_idx = np.nonzero(data)[0]
    first_bin = valid_idx[0]
    last_bin = valid_idx[-1]

    max_ent = -9999999999999999999999
    threshold = -1
    ent_values = np.zeros(256)

    for it in range(first_bin, last_bin + 1):
        ent_back = 0.0;
        for ih in range (it+1):
            if data[ih] != 0:
                ent_back -= ( norm_histo[ih] / P1[it] ) * np.log( norm_histo[ih] / P1[it] );

        ent_obj = 0.0;
        for ih in range (it+1,256):
            if data[ih] != 0:
                ent_obj -= ( norm_histo[ih] / P2[it] ) * np.log( norm_histo[ih] / P2[it] );

        tot_ent = ent_back + ent_obj;
        ent_values[it] = tot_ent
        if max_ent < tot_ent:
            max_ent = tot_ent;
            threshold = it;   

    return threshold,ent_values;


def renyi_entropy_imageJ(data):
    total = data.sum()

    norm_histo = data / total

    P1 = np.zeros(len(norm_histo))
    P2 = np.zeros(len(norm_histo))
    #P1 = np.copy(norm_histo)\
    P1[0]=norm_histo[0];
    P2[0]=1.0-P1[0];

    for ih in range(len(norm_histo)):
        P1[ih]= P1[ih-1] + norm_histo[ih];
        P2[ih]= 1.0 - P1[ih];


    valid_idx = np.nonzero(data)[0]
    first_bin = valid_idx[0]
    last_bin = valid_idx[-1]


    # Maximum Entropy Thresholding - BEGIN 
    # ALPHA = 1.0 
    # Calculate the total entropy each gray-level and find the threshold that maximizes it 
    ent_values_2 = np.zeros(256)      
    max_ent = -9999999999999999999999
    threshold = -1
    for it in range(first_bin, last_bin + 1):
        ent_back = 0.0;
        for ih in range (it+1):
            if data[ih] != 0:
                ent_back -= ( norm_histo[ih] / P1[it] ) * np.log( norm_histo[ih] / P1[it] );

        ent_obj = 0.0;
        for ih in range (it+1,256):
            if data[ih] != 0:
                ent_obj -= ( norm_histo[ih] / P2[it] ) * np.log( norm_histo[ih] / P2[it] );

        tot_ent = ent_back + ent_obj;
        ent_values_2[it] = tot_ent
        if max_ent < tot_ent:
            max_ent = tot_ent;
            threshold = it;
        
    t_star2 = threshold;

    # Maximum Entropy Thresholding - END

    threshold =0
    max_ent = 0.0;
    alpha = 0.5;
    term = 1.0 / ( 1.0 - alpha );
    ent_values_1 = np.zeros(256)      

    for it in range(first_bin, last_bin + 1):
        
        ent_back = 0.0;
        for ih in range (it+1):
            ent_back += np.sqrt( norm_histo[ih] / P1[it] );

        ent_obj = 0.0;

        for ih in range (it+1,256):
            ent_obj += np.sqrt ( norm_histo[ih] / P2[it] );

        #tot_ent =  np.log ( ent_back * ent_obj ) if term * ( ( ent_back * ent_obj ) > 0.0 else  0.0);
        tot_ent =  term *np.log( ent_back * ent_obj ) if  ( ent_back * ent_obj ) > 0.0 else  0.0
        ent_values_1[it] = tot_ent  

        if max_ent < tot_ent:
            max_ent = tot_ent;
            threshold = it;

    t_star1 = threshold;
    

    threshold = 0; 
    max_ent = 0.0;
    alpha = 2.0;
    term = 1.0 / ( 1.0 - alpha );
    ent_values_3 = np.zeros(256)      

    for it in range(first_bin, last_bin + 1):
        ent_back = 0.0;
        for ih in range (it+1):
            ent_back += ( norm_histo[ih] * norm_histo[ih] ) / ( P1[it] * P1[it] );

        ent_obj = 0.0;

        for ih in range (it+1,256):
            ent_obj += ( norm_histo[ih] * norm_histo[ih] ) / ( P2[it] * P2[it] );

        tot_ent = term *np.log(ent_back * ent_obj ) if ( ent_back * ent_obj ) > 0.0 else 0.0
        ent_values_3[it] = tot_ent

        if max_ent < tot_ent:
            max_ent = tot_ent;
            threshold = it;

    t_star3 = threshold;

    t_star1, t_star2,t_star3 = sorted([t_star1, t_star2,t_star3])

    if (np.abs(t_star1 -t_star2) <= 5):
        if (np.abs(t_star2 -t_star3) <=5):
            beta1,beta2,beta3 = 1,2,1
        else:
            beta1,beta2,beta3 = 0,1,3
    else:
        if (np.abs(t_star2 -t_star3) <=5):
            beta1,beta2,beta3 = 3,1,0
        else:
            beta1,beta2,beta3 = 1,2,1

    omega = P1[t_star3] - P1[t_star1];
    opt_threshold = (int) (t_star1 * ( P1[t_star1] + 0.25 * omega * beta1 ) + 0.25 * t_star2 * omega * beta2  + t_star3 * ( P2[t_star3] + 0.25 * omega * beta3 ));

    return threshold, ent_values_1,ent_values_2,ent_values_3

def MP_ACT(mask_image, ori_image, micrometer_per_pix, filename=None):  # filename is now optional
    mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2GRAY)
    ori_image_labeled = np.copy(ori_image)
    
    contour_list_cv2, hierarchy = cv2.findContours(mask_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    mp_shape_name = ["Fibers", "Fragments", "Particles"]
    mp_shape_count = {"Fibers": 0, "Fragments": 0, "Particles": 0, "None": 0}

    # Only prepare file writing if filename was provided
    if filename is not None:
        f_out = open(filename, "w")  # Use the parameter name 'filename' not 'file_name'
        f_out.write("Index,Shape,Location x,Location y,Area,Feret Diameter,Feret Degree,Circulariy,Roundness,Perimeter\n")

    for index, contour in enumerate(contour_list_cv2[1:]):
        rect = cv2.boundingRect(contour)
        x, y, w, h = rect

        reshaped_contour = contour.reshape((contour.shape[0], contour.shape[-1]))
        # Изчисляване на квадратни разстояния
        feret_diameters = distance.cdist(reshaped_contour, reshaped_contour, 'sqeuclidean')
        # Намиране на индекси на точките с максимално разстояние
        (a, b) = np.unravel_index(feret_diameters.argmax(), feret_diameters.shape)
        point_a = reshaped_contour[a]
        point_b = reshaped_contour[b]

        # Преобразуване на квадратно разстояние в линейно
        max_distance = np.sqrt(feret_diameters.max())
        # Ъгъл на максималния диаметър (Feret Degree)
        deltaY = point_a[1] - point_b[1]
        deltaX = point_a[0] - point_b[0]
        angleInDegrees = np.arctan2(deltaY, deltaX) * 180 / np.pi
        # Изчисляване на площ и периметър
        area = cv2.contourArea(contour)
        peri = cv2.arcLength(contour, False)
        # Начертаване на линията за Feret Diameter, ако площта е значителна
        if area > 20:
            ori_image_labeled = cv2.line(ori_image_labeled, tuple(point_a), tuple(point_b), (0, 0, 255), 2)

        if area < 3:
            continue

        cv2.rectangle(ori_image_labeled, (x, y), (x + w, y + h), (0, 255, 0), 1)
        # Преизчисляване на кръглост и кръговост с линейното разстояние
        round_shape = 4 * area / (np.pi * np.power(max_distance, 2))
        circularity = 4 * np.pi * (area / np.power(peri, 2))
        # Класификация по форма
        mp_shape = "None"
        if min(0, 0.3) <= circularity < max(0, 0.3):
            mp_shape = "Fibers"
        elif min(0.3, 0.7) <= circularity < max(0.3, 0.7):
            mp_shape = "Fragments"
        else:
            mp_shape = "Particles"

        mp_shape_count[mp_shape] += 1
        dy=13

        cv2.putText(ori_image_labeled,str(index),(x+w+10,y+h),0,0.5,(0,255,0))
        cv2.putText(ori_image_labeled,"type: "+mp_shape,(x+w+10,y+h+dy),0,0.5,(0,255,0))
        cv2.putText(ori_image_labeled,"feret: "+str(max_distance *micrometer_per_pix)[:4],(x+w+10,y+h+dy*2),0,0.5,(0,255,0))
        # Запис в изходния файл
        # Only write to file if filename was provided
        if filename is not None:
            f_out.write(
                str(index) + "," + str(mp_shape) + "," + str(x + w * 0.5) + "," + str(y + h * 0.5) + "," +
                str(area * micrometer_per_pix * micrometer_per_pix) + "," +
                str(max_distance * micrometer_per_pix) + "," + str(angleInDegrees) + "," +
                str(circularity) + "," + str(round_shape) + "," + str(peri * micrometer_per_pix) + "\n"
            )

    # Only write summary and close file if filename was provided
    if filename is not None:
        f_out.write("\n")
        f_out.write("None:"+str(mp_shape_count["None"])+"\n")
        f_out.write("Fibers:"+str(mp_shape_count["Fibers"])+"\n")
        f_out.write("Fragments:"+str(mp_shape_count["Fragments"])+"\n")
        f_out.write("Particles:"+str(mp_shape_count["Particles"])+"\n")
        f_out.close()
        
    return ori_image_labeled

def add_grid(ori_image_labeled, file_name):
    # 나중에 추가할 코드 
    temp_file_name = "temp.png"
    cv2.imwrite(temp_file_name,cv2.cvtColor(ori_image_labeled, cv2.COLOR_BGR2RGB))
    img_plt = plt.imread(temp_file_name)
    height, width, depth = img_plt.shape
    figsize = width / float(300)+2, height / float(300)+2
    plt.figure(figsize=figsize)

    imgplot = plt.imshow(img_plt)
    plt.grid(linewidth=0.2)
    plt.savefig(file_name,dpi= 300)

def MP_VAT(ori_image):
    return thresholding(ori_image, max_entropy_imageJ)

def MP_VAT_2(ori_image):
    return thresholding(ori_image, renyi_entropy_imageJ)

def custom_thresholding(ori_image, value):
    fixed_val_function = lambda any_item: [value]
    return thresholding(ori_image, fixed_val_function)

def thresholding(ori_image, treshold_function):
    ori_image = ~ori_image #invert
    im = Image.fromarray(ori_image.astype(np.uint8))
    im = im.convert('L') #8bit
    im = np.array(im)

    # obtain histogram
    hist = np.histogram(im, bins=256, range=(0, 256))[0]
    # get threshold
    th = treshold_function(hist)
    im[im>th[0]] = 255
    im[im<=th[0]] = 0# masked image

    
    im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)

    return im
