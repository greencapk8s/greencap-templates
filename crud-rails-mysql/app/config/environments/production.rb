Rails.application.configure do
  config.enable_reloading = false
  config.eager_load = true
  config.consider_all_requests_local = false

  # Serve the stylesheet straight from public/ — this Template deliberately skips
  # the asset pipeline to stay minimal. Enabled via RAILS_SERVE_STATIC_FILES.
  config.public_file_server.enabled = ENV["RAILS_SERVE_STATIC_FILES"].present?

  config.log_level = :info
  config.logger = ActiveSupport::Logger.new(STDOUT) if ENV["RAILS_LOG_TO_STDOUT"].present?

  config.active_record.dump_schema_after_migration = false
end
