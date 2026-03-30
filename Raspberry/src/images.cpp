#include <opencv2/opencv.hpp>
#include <iostream>


int main(){

    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "Erreur" << std::endl;
        return -1;
    }

    cv::Mat frame, hsv;
    cv::Mat masque_bleu, masque_rouge, masque_vert;
    cv::Mat masque_bleuBGR;

    cv::Scalar bleuHaut(110,255,255), BleuBas(88,111,10);

    cv::Mat affichage = cv::Mat::zeros(480,1280, CV_8UC3);
    cv::Rect gauche(0,0,640,480);
    cv::Rect droite(640,0,640,480);


    while(true){
        cap >> frame;
        if (frame.empty()) continue;

        cv::resize(frame, frame, cv::Size(640, 480));
        cv::cvtColor(frame, hsv, cv::COLOR_BGR2HSV);

        cv::inRange(hsv, BleuBas, bleuHaut, masque_bleu);

        cv::cvtColor(masque_bleu, masque_bleuBGR, cv::COLOR_GRAY2BGR);

        frame.copyTo(affichage(gauche));
        masque_bleuBGR.copyTo(affichage(droite));
        

        cv::imshow("Bleu", affichage);

        if (cv::waitKey(30) == 27) break;
    }
    return 0;
}