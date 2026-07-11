require_relative "boot"

require "rails"
# Load only the frameworks this Template needs — no Active Job, Action Mailer,
# Action Cable, or Active Storage — to keep the study app small and legible.
require "active_model/railtie"
require "active_record/railtie"
require "action_controller/railtie"
require "action_view/railtie"

Bundler.require(*Rails.groups)

module CrudRailsMysql
  class Application < Rails::Application
    config.load_defaults 7.1
  end
end
