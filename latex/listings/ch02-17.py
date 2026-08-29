output = relu(matmul(input, W) + b)
#        ^          ^            ^
#        |          |            +-- addition (with broadcasting)
#        |          +--------------- tensor product
#        +-------------------------- element-wise operation
