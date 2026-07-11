Rails.application.routes.draw do
  root "items#index"
  resources :items, except: [:show]
end
