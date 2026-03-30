#include <opencv2/opencv.hpp>
#include <iostream>
#include <chrono>

int main() {
    using namespace std::chrono;

    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "Erreur : Impossible d'ouvrir la caméra" << std::endl;
        return -1;
    }

    cv::Mat frame, hsv;
    cv::Mat masque_orange, masque_jaune, masque_bleu;
    cv::Mat sortie;

    // Plages HSV (ajuster si besoin selon lumière / cam)
    cv::Scalar orangeBas(5, 100, 100), orangeHaut(18, 255, 255);
    cv::Scalar jauneBas(20, 100, 100), jauneHaut(35, 255, 255);
	cv::Scalar bleuBas(88, 111, 10), bleuHaut(110, 255, 255);

    auto dernierCapture = steady_clock::now() - milliseconds(500);

    // On conserve le dernier résultat traité pour l'afficher le plus fréquemment possible
    cv::Mat resultat;

    while (true) {
        auto maintenant = steady_clock::now();
        char t = (char)cv::waitKey(30); // affichage réactif, lecture de touche franche
        if (t == 27) break; // Esc pour sortir

        if (maintenant - dernierCapture >= milliseconds(500)) {
            // Capturer et traiter seulement toutes les 0,5 s
            cap >> frame;
            if (!frame.empty()) {
                cv::resize(frame, frame, cv::Size(640, 480));
                cv::cvtColor(frame, hsv, cv::COLOR_BGR2HSV);

                cv::inRange(hsv, orangeBas, orangeHaut, masque_orange);
                cv::inRange(hsv, jauneBas, jauneHaut, masque_jaune);
                cv::inRange(hsv, bleuBas, bleuHaut, masque_bleu);

                sortie = cv::Mat::zeros(frame.size(), frame.type());
                sortie.setTo(cv::Scalar(0, 165, 255), masque_orange);
                sortie.setTo(cv::Scalar(0, 255, 255), masque_jaune);
                sortie.setTo(cv::Scalar(255, 0, 0), masque_bleu);

                resultat = sortie;
                dernierCapture = maintenant;
            }
        }

        if (!resultat.empty()) {
            cv::imshow("Original", frame);
            cv::imshow("Zones orange/jaune/bleu sur fond noir", resultat);
        }
    }

    return 0;
}
