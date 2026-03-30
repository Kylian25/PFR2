#include <opencv2/opencv.hpp>
#include <iostream>

// Valeurs initiales (on commence large)
int h_min = 0, s_min = 0, v_min = 0;
int h_max = 179, s_max = 255, v_max = 255;

int main() {
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) return -1;

    // 1. Créer une fenêtre pour les contrôles
    cv::namedWindow("Controle", cv::WINDOW_AUTOSIZE);
    
    // 2. Ajouter les curseurs (Trackbars)
    cv::createTrackbar("H Min", "Controle", &h_min, 179);
    cv::createTrackbar("H Max", "Controle", &h_max, 179);
    cv::createTrackbar("S Min", "Controle", &s_min, 255);
    cv::createTrackbar("S Max", "Controle", &s_max, 255);
    cv::createTrackbar("V Min", "Controle", &v_min, 255);
    cv::createTrackbar("V Max", "Controle", &v_max, 255);

    cv::Mat frame, hsv, mask, maskBGR, canvas;
    canvas = cv::Mat::zeros(480, 1280, CV_8UC3);

    while (true) {
        cap >> frame;
        if (frame.empty()) continue;

        cv::resize(frame, frame, cv::Size(640, 480));
        cv::cvtColor(frame, hsv, cv::COLOR_BGR2HSV);

        // 3. Utiliser les variables liées aux curseurs
        cv::Scalar bas(h_min, s_min, v_min);
        cv::Scalar haut(h_max, s_max, v_max);
        
        // Sécurité pour éviter le crash Bas > Haut
        if (h_min > h_max) cv::setTrackbarPos("H Min", "Controle", h_max);
        if (s_min > s_max) cv::setTrackbarPos("S Min", "Controle", s_max);
        if (v_min > v_max) cv::setTrackbarPos("V Min", "Controle", v_max);

        cv::inRange(hsv, bas, haut, mask);

        // 4. Affichage côte à côte
        cv::cvtColor(mask, maskBGR, cv::COLOR_GRAY2BGR);
        frame.copyTo(canvas(cv::Rect(0, 0, 640, 480)));
        maskBGR.copyTo(canvas(cv::Rect(640, 0, 640, 480)));

        cv::imshow("Calibration HSV", canvas);

        if (cv::waitKey(30) == 27) {
            // Affiche les valeurs finales dans la console avant de quitter
            std::cout << "Valeurs trouvees : " << std::endl;
            std::cout << "Bas : (" << h_min << "," << s_min << "," << v_min << ")" << std::endl;
            std::cout << "Haut : (" << h_max << "," << s_max << "," << v_max << ")" << std::endl;
            break;
        }
    }
    return 0;
}