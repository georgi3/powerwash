#!/bin/bash
# copy_react_build.sh

# Build the React app
cd "$HOME"/Documents/powerwash/ || exit
npm run build
DJANGO_PROJECT_PATH="$HOME/Documents/nativeWash"

# Create target directories in STATICFILES_DIRS
target_dir="${DJANGO_PROJECT_PATH}/calculator/build/static"
mkdir -p "${target_dir}/js"
mkdir -p "${target_dir}/css"

# Copy and rename the main JS file (with simplified names)
cp build/static/js/main.*.js "${target_dir}/js/price-calculator.js"
cp build/static/css/main.*.css "${target_dir}/css/price-calculator.css"

# Run collectstatic to copy to STATIC_ROOT
cd ${DJANGO_PROJECT_PATH} || exit
python manage.py collectstatic --noinput

echo "React build files copied and collected for Django"