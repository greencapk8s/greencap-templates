FROM ruby:3.3-slim

# mysql2 compiles a native extension, so it needs the MySQL client library and a
# build toolchain present at image-build time.
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV RAILS_ENV=production \
    BUNDLE_WITHOUT=development:test \
    RAILS_LOG_TO_STDOUT=true \
    RAILS_SERVE_STATIC_FILES=true

COPY Gemfile ./
RUN bundle install

COPY . .

EXPOSE 3000

CMD ["sh", "./entrypoint.sh"]
