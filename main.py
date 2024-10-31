import cv2
import csv
import cvzone
import time  # Import the time module
from cvzone.HandTrackingModule import HandDetector

# Open the camera (index 0)
cap = cv2.VideoCapture(0)
# Set frame width and height
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

# Initialize the hand detector
detector = HandDetector(detectionCon=0.8)

# Define a class for checking the right answer
class Quiz:
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])
        self.userans = None

    def update(self, cursor, boxes):
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box
            # Add padding to the boxes for easier clicking
            padding = 20
            x1 -= padding
            y1 -= padding
            x2 += padding
            y2 += padding

            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userans = i + 1
                # Visual feedback for the selected answer
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)
                print(f"Answer {i + 1} selected")

# Import CSV file
pathCSV = "quiz.csv"
with open(pathCSV) as f:
    reader = csv.reader(f)
    dataall = list(reader)[1:]

# Create quiz objects
quizList = [Quiz(q) for q in dataall]
print(f"Total questions: {len(quizList)}")

# Initialize question number, total questions, and score
qNo = 0
qtotal = len(quizList)
score = 0  # Variable to track score

# Main loop
while True:
    # Capture the frame
    success, img = cap.read()
    if not success:
        break

    # Flip the camera view
    img = cv2.flip(img, 1)

    # Hand detection
    hands, img = detector.findHands(img, flipType=False)

    # Display question and answer choices on screen
    if qNo < qtotal:
        quiz = quizList[qNo]
        img, box = cvzone.putTextRect(img, quiz.question, [50, 100], 2, 3, border=5)
        img, box1 = cvzone.putTextRect(img, "1. " + quiz.choice1, [50, 200], 2, 3, border=5)
        img, box2 = cvzone.putTextRect(img, "2. " + quiz.choice2, [50, 300], 2, 3, border=5)
        img, box3 = cvzone.putTextRect(img, "3. " + quiz.choice3, [50, 400], 2, 3, border=5)
        img, box4 = cvzone.putTextRect(img, "4. " + quiz.choice4, [50, 500], 2, 3, border=5)

    # Check for hand landmarks if hands are detected
    if hands:
        lmList = hands[0]['lmList']  # Get the list of hand landmarks
        cursor = lmList[8][:2]  # Extract only x and y for index finger tip
        length, info, img = detector.findDistance(lmList[8][:2], lmList[12][:2], img)  # Calculate distance between index and middle finger tips

        if length < 60:
            quiz.update(cursor, [box1, box2, box3, box4])
            
            # Move to the next question if an answer is selected
            if quiz.userans is not None:
                # Check if the selected answer is correct
                if quiz.userans == quiz.answer:
                    print("Correct answer!")
                    score += 1  # Increment score for correct answer
                else:
                    print("Wrong answer!")
                
                # Clear user answer and increment question number
                quiz.userans = None
                
                # Delay before moving to the next question
                time.sleep(0.8)  # Adjust the delay as needed
                qNo += 1  # Move to the next question
                if qNo >= qtotal:
                    print("Quiz completed!")
                    break  # Exit the loop to display the final score

    # Draw the progress bar
    bar_length = 1000  # Length of the progress bar
    bar_height = 50    # Height of the progress bar
    progress = int((qNo / qtotal) * bar_length)  # Calculate the progress based on questions answered

    # Draw filled progress bar
    cv2.rectangle(img, (150, 600), (150 + progress, 600 + bar_height), (0, 255, 0), cv2.FILLED)
    # Draw the border of the progress bar
    cv2.rectangle(img, (150, 600), (1150, 600 + bar_height), (255, 0, 255), 5)

    # Display the resulting frame
    cv2.imshow("IMG", img)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Display final score
img.fill(0)  # Clear the image
final_message = f"Quiz completed! Your score: {score}/{qtotal}"
cv2.putText(img, final_message, (150, 360), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3, cv2.LINE_AA)
cv2.imshow("Final Score", img)
cv2.waitKey(5000)  # Show the final score for 5 seconds

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
