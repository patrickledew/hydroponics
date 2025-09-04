tmux \
    new-session  'nodemon --exec "flask --app main run --host=0.0.0.0" -e py' \; \
    split-window 'cd client && npm run dev -- --host' \;
