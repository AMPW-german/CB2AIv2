import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
import csv
import torch
import torch.nn as nn
import torch.optim as optim

class CB2AIv2(nn.Module):
    def __init__(self, input_dim, num_buttons):
        super(CB2AIv2, self).__init__()
        
        # Define the network layers
        self.fc1 = nn.Linear(input_dim, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc2 = nn.Linear(256, 128)
        
        # Output layer for joystick (continuous)
        self.joystick_output = nn.Linear(128, 1)  # Continuous value
        
        # Output layer for buttons (binary)
        self.buttons_output = nn.Linear(128, num_buttons)  # Binary output for each button
    
    def forward(self, x):
        # Pass through the layers
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        
        # Get joystick prediction (continuous)
        #joystick = self.joystick_output(x)
        joystick = torch.sigmoid(self.joystick_output(x))
        
        # Get buttons prediction (binary classification)
        buttons = torch.sigmoid(self.buttons_output(x))  # Sigmoid for binary output
        
        return joystick, buttons

def train():
    observations = []
    class_ids = []
    track_ids = []
    health = []
    joystick = []
    buttons = []

    DIR = r".\\ai\\"

    with open(f"{DIR}ai.csv", "r") as f:
        reader = csv.reader(f)

        for row in reader:
            if row == []:
                continue

            observation = list(row[13:])
            obs = []
            classes = []
            tracks = []
            i = 0
            while i < len(observation):
                obs.append([float(observation[i]), float(observation[i + 1]), float(observation[i + 2]), float(observation[i + 3]), float(observation[i + 6])])
                classes.append(int(float(observation[i + 4])))
                tracks.append(int(float(observation[i + 5])))
                i += 7

            observations.append([j for i in obs for j in i])

            class_ids.append(classes)
            track_ids.append(tracks)

            health.append(float(row[12]))
            joystick.append(float(row[1]) / 360)
            buttons.append([True if i == "True" else False for i in row[2:8]])
            
    one_hot_encoder = OneHotEncoder(sparse_output=False)
    class_ids = np.array(class_ids)
    track_ids = np.array(track_ids)
    joystick = np.array(joystick)
    health = np.array(health).reshape(-1, 1)
    class_ids_encoded = one_hot_encoder.fit_transform(class_ids.reshape(-1, 1))
    track_ids_encoded = one_hot_encoder.fit_transform(track_ids.reshape(-1, 1))

    observations_augmented = np.hstack([observations, class_ids, track_ids, health])

    actions = np.hstack([joystick.reshape(-1, 1), buttons])

    observations_train, observations_val, actions_train, actions_val = train_test_split(
        observations_augmented, actions, test_size=0.2, random_state=42
    )

    # Hyperparameters
    learning_rate = 0.0001
    batch_size = 256
    num_epochs = 5000
    num_buttons = 6  # Adjust according to the number of buttons

    observations_train_tensor = torch.tensor(observations_train, dtype=torch.float32)
    actions_joystick_train_tensor = torch.tensor(actions_train[:, :1], dtype=torch.float32).view(-1, 1)
    actions_buttons_train_tensor = torch.tensor(actions_train[:, 1:], dtype=torch.float32)

    input_dim = observations_augmented.shape[1]
    print(input_dim)
    model = CB2AIv2(input_dim=input_dim, num_buttons=num_buttons)

    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Loss functions
    joystick_loss_fn = nn.MSELoss()  # For joystick (continuous output)
    buttons_loss_fn = nn.BCELoss()   # For buttons (binary classification)

    # Training Loop
    for epoch in range(num_epochs):
        model.train()  # Set the model to training mode
        
        # Zero the gradients
        optimizer.zero_grad()
        
        # Forward pass
        joystick_preds, button_preds = model(observations_train_tensor)
        
        # Compute the losses
        joystick_loss = joystick_loss_fn(joystick_preds.squeeze(), actions_joystick_train_tensor.squeeze())
        buttons_loss = buttons_loss_fn(button_preds, actions_buttons_train_tensor)
        
        # Total loss is the sum of both losses
        total_loss = joystick_loss + buttons_loss
        
        # Backward pass (compute gradients)
        total_loss.backward()
        
        # Update weights
        optimizer.step()
        
        # Print statistics every few epochs
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}], Joystick Loss: {joystick_loss.item():.4f}, Buttons Loss: {buttons_loss.item():.4f}")


    torch.save(model.state_dict(), r'.\\ai\\final_model.pth')
    print("Final model saved!")


def predictor(image_count_name, pause_name, done_name, user_input_name, degree_name, keyboard_button_name, keyboard_button_shape, health_percent_name, yolo_name, yolo_shape):
    import multiprocessing.shared_memory as shared_memory
    
    image_count_dtype = np.uint32
    pause_dtype = np.bool_
    done_dtype = np.bool_
    user_input_dtype = np.bool_
    degree_dtype = np.double
    keyboard_button_dtype = np.bool_
    health_percent_dtype = np.float32
    yolo_dtype = np.float32

    image_count_shm = shared_memory.SharedMemory(name=image_count_name)
    pause_shm = shared_memory.SharedMemory(name=pause_name)
    done_shm = shared_memory.SharedMemory(name=done_name)
    user_input_shm = shared_memory.SharedMemory(name=user_input_name)
    degree_shm = shared_memory.SharedMemory(name=degree_name)
    keyboard_button_shm = shared_memory.SharedMemory(name=keyboard_button_name)
    health_percent_shm = shared_memory.SharedMemory(name=health_percent_name)
    yolo_shm = shared_memory.SharedMemory(name=yolo_name)
    
    image_count = np.ndarray((1,), dtype=image_count_dtype, buffer=image_count_shm.buf)
    pause = np.ndarray((1,), dtype=pause_dtype, buffer=pause_shm.buf)
    done = np.ndarray((1,), dtype=done_dtype, buffer=done_shm.buf)
    user_input = np.ndarray((1,), dtype=user_input_dtype, buffer=user_input_shm.buf)
    degree = np.ndarray((1,), dtype=degree_dtype, buffer=degree_shm.buf)
    keyboard_button = np.ndarray(keyboard_button_shape, dtype=keyboard_button_dtype, buffer=keyboard_button_shm.buf)
    health_percent = np.ndarray((1,), dtype=health_percent_dtype, buffer=health_percent_shm.buf)
    image_count_old = image_count[0]
    yolo = np.ndarray(yolo_shape, dtype=yolo_dtype, buffer=yolo_shm.buf)
    
    model = CB2AIv2(701, 6)

    model.load_state_dict(torch.load(r".\\ai\\final_model.pth"))

    model.eval()

    while 1:
        if image_count[0] > image_count_old + 5 and not pause:
            image_count_old = image_count[0]

            input_array = np.concatenate((np.array(yolo[:, :4].flatten()), np.array(yolo[:, 6].flatten()), np.array(yolo[:, 4:6].flatten()), np.array(health_percent[0]).reshape(1,)))

            input_tensor = torch.tensor(input_array, dtype=torch.float32)
            input_tensor = input_tensor.unsqueeze(0)

            with torch.no_grad():
                joystick_preds, button_preds = model(input_tensor)
                print("Joystick Prediction:", joystick_preds.numpy()[0][0] * 360)
                print("Button Predictions:", [True if button_pred >= 0.5 else False for button_pred in button_preds.numpy()[0]])
        
        if done:
            break

if __name__ == "__main__":
    train()