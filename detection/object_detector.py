import cv2
import numpy as np

class ObjectDetector:
    def __init__(self):
        pass

    def detect(self, frame):
        # Obtener las dimensiones de la pantalla
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        # Definir el radio del círculo centrado en la pantalla
        radius = min(width, height) // 4  # Puedes ajustar el radio según tus necesidades

        # Convertir la imagen a escala de grises
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Aplicar un umbral para encontrar áreas brillantes
        _, thresh = cv2.threshold(gray_frame, 200, 255, cv2.THRESH_BINARY)

        # Encontrar contornos en la imagen umbralizada
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        for contour in contours:
            # Filtrar los contornos pequeños en función del área
            area = cv2.contourArea(contour)
            if area > 1000:  # Ajusta este umbral según tus necesidades
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calcular el centro del contorno
                obj_center_x = x + w // 2
                obj_center_y = y + h // 2
                
                # Calcular la distancia desde el centro del objeto al centro de la pantalla
                distance = np.sqrt((obj_center_x - center_x) ** 2 + (obj_center_y - center_y) ** 2)

                # Comprobar si el centro del objeto está dentro del círculo
                if distance <= radius:
                    detections.append((x, y, w, h))

        return detections
