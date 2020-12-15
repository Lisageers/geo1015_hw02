#-- my_code_hw02.py
#-- Assignment 02 GEO1015.2020
#-- [YOUR NAME] 
#-- [YOUR STUDENT NUMBER] 
#-- [YOUR NAME] 
#-- [YOUR STUDENT NUMBER] 

import sys
import math
import numpy
import rasterio
from rasterio import features



def output_viewshed(d, viewpoints, maxdistance, output_file):
    """
    !!! TO BE COMPLETED !!!
     
    Function that writes the output raster
     
    Input:
        d:            the input datasets (rasterio format)  
        viewpoints:   a list of the viewpoints (x, y, height)
        maxdistance:  max distance one can see
        output_file:  path of the file to write as output
        
    Output:
        none (but output GeoTIFF file written to 'output-file')
    """  
    

    #-- numpy of input
    npi  = d.read(1)
    print(npi.shape)
    #-- the results of the viewshed in npvs, all values=3
    npvs = numpy.zeros(d.shape, dtype=numpy.int8)
    npvs = npvs + 3

    # loop through grid
    for row in range(len(npvs)):
        for column in range(len(npvs[0])):
            # get coordinates of the pixel
            cor = d.xy(row, column)
            
            # loop through viewpoints
            for vpoint in viewpoints:
                # check if pixel is in range
                if math.sqrt((cor[0] - vpoint[0]) ** 2 + (cor[1] - vpoint[1]) ** 2) <= maxdistance:
                    npvs[row , column] = 0
    
    vrow, vcol = d.index(viewpoints[0][0], viewpoints[0][1])

    range_indices = numpy.argwhere(npvs == 0)
    for i in range_indices:
        line = bresenham_line(d, viewpoints[0], (i[0], i[1]))
        line_indices = numpy.argwhere(line == 1)
        if i[0] < vrow:
            line_indices = line_indices[::-1]
        tan = 0
        # loop through indices
        for index in line_indices:
            # get z, coordinates and distance of index
            z = npi[index[0], index[1]]
            cor = d.xy(index[0], index[1])
            distance = math.sqrt((cor[0] - viewpoints[0][0]) ** 2 + (cor[1] - viewpoints[0][1]) ** 2)
            # calculate z difference
            z_diff = z - (viewpoints[0][2] + npi[vrow, vcol])
            
            # pixel not visible if angle is smaller 
            if math.atan(z_diff/distance) < tan:
                npvs[index[0] , index[1]] = 0
            else:
                # pixel visible if tan is larger and update tan
                tan = math.atan(z_diff/distance)
                npvs[index[0] , index[1]] = 1
    
    
    # add viewpoints
    for point in viewpoints:
        # get indexes
        vrow, vcol = d.index(point[0], point[1])
        # set value
        npvs[vrow , vcol] = 2

    #-- write this to disk
    with rasterio.open(output_file, 'w', 
                       driver='GTiff', 
                       height=npi.shape[0],
                       width=npi.shape[1], 
                       count=1, 
                       dtype=rasterio.uint8,
                       crs=d.crs, 
                       transform=d.transform) as dst:
        dst.write(npvs.astype(rasterio.uint8), 1)

    print("Viewshed file written to '%s'" % output_file)



def bresenham_line(d, vp, q):
    # d = rasterio dataset as above
    # a = (10, 10)
    # b = (100, 50)
    #-- create in-memory a simple GeoJSON LineString
    v = {}
    v["type"] = "LineString"
    v["coordinates"] = []
    v["coordinates"].append((vp[0], vp[1]))
    v["coordinates"].append(d.xy(q[0], q[1]))
    shapes = [(v, 1)]
    re = features.rasterize(shapes, 
                            out_shape=d.shape, 
                            # all_touched=True,
                            transform=d.transform)
    return re
    # re is a numpy with d.shape where the line is rasterised (values != 0)



