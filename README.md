ЗАПУСК
    
    git clone https://github.com/phantom-profile/polling_service.git
    docker build -t polling-service .
    docker run --rm -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY polling-service
