from data import get_mnist
import numpy as np
import matplotlib.pyplot as plt

"""
w = weights, b = bias, i = input, h = hidden, o = output, l = label
"""
images, labels = get_mnist()
w_i_h = np.random.randn(100, 784) * np.sqrt(1 / 784)  # 100 hidden neurons, 784 input neurons
w_h_o = np.random.randn(10, 100) * np.sqrt(1 / 30)  # 10 output neurons, 100 hidden neurons
b_i_h = np.zeros((100, 1))  # 100 hidden neurons
b_h_o = np.zeros((10, 1))  # 10 output neurons

learn_rate = 0.01
nr_correct = 0
epochs = 200
for epoch in range(epochs):
    for img, l in zip(images, labels):
        img.shape += (1,) # makes it from a vector to a matrix
        l.shape += (1,) # makes it from a vector to a matrix
        #forward propagation input -> hidden
        h_pre = b_i_h + w_i_h @ img
        h = 1 / (1 + np.exp(-h_pre))
        #forward propagation hidden -> output
        o_pre = b_h_o + w_h_o @ h
        o = 1 / (1 + np.exp(-o_pre))

        # cost / error calculation
        e = -np.sum(l * np.log(o + 1e-8))
        nr_correct += int(np.argmax(o) == np.argmax(l))

        # backpropagation output -> hidden (cost function derivative)
        delta_o = o - l  # Correct gradient for output layer
        w_h_o += -learn_rate * delta_o @ np.transpose(h)
        b_h_o += -learn_rate * delta_o

        # backpropagation hidden -> input (cost function derivative)
        delta_h = np.transpose(w_h_o) @ delta_o * (h * (1 - h))
        w_i_h += -learn_rate * delta_h @ np.transpose(img)
        b_i_h += -learn_rate * delta_h

    # show accuracy after each epoch
    print(f"epoch: {(epoch + 1)} Acc: {(nr_correct / images.shape[0]) * 100}%")
    if nr_correct / images.shape[0] == 1:
        print("All images classified correctly")
        break
    nr_correct = 0

# Show misclassified results
misclassified_indices = []

for index, (img, label) in enumerate(zip(images, labels)):
    img = img.reshape(784, 1)  # Ensure the image is in matrix form
    # Forward propagation input -> hidden
    h_pre = b_i_h + w_i_h @ img
    h = 1 / (1 + np.exp(-h_pre))
    # Forward propagation hidden -> output
    o_pre = b_h_o + w_h_o @ h
    o = 1 / (1 + np.exp(-o_pre))

    if o.argmax() != label.argmax():
        misclassified_indices.append(index)

print(f"Number of misclassified images: {len(misclassified_indices)}")