import numpy as np

# Your current matrices
cost_matrix = np.array([
    [  0.  , 104.85, 110.9 , 117.25,  98.75],
    [ 91.5 ,   0.  ,  72.7 , 100.2 ,  90.5 ],
    [   np.inf,  73.2 ,   0.  ,  67.5 ,  99.6 ],
    [107.1 , 102.9 ,  62.7 ,   0.  ,  94.6 ],
    [ 95.5 , 106.4 ,    np.inf, 109.9 ,   0.  ]
])

time_matrix = np.array([
    [ 0.        ,  4.75      ,  3.83333333,  9.5       ,  1.83333333],
    [ 4.58333333,  0.        ,  2.75      ,  2.9       ,  4.75      ],
    [        np.inf,  2.75      ,  0.        ,  2.75      , 11.08333333],
    [16.33333333,  3.16666667,  2.91666667,  0.        ,  3.33333333],
    [13.58333333,  4.16666667,         np.inf, 17.33333333,  0.        ]
])

# Fill missing values using reverse routes
# Berlin -> London: use London -> Berlin
cost_matrix[2][0] = cost_matrix[0][2]  # 110.9
time_matrix[2][0] = time_matrix[0][2]  # 3.83

# Copenhagen -> Berlin: use Berlin -> Copenhagen
cost_matrix[4][2] = cost_matrix[2][4]  # 99.6
time_matrix[4][2] = time_matrix[2][4]  # 11.08

print("Cost Matrix (£):")
print(cost_matrix)
print("\nTime Matrix (hours):")
print(time_matrix)
