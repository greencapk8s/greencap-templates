class ItemsController < ApplicationController
  def index
    @items = Item.order(:id)
  end

  def new
    @item = Item.new
  end

  def create
    Item.create(item_params)
    redirect_to root_path
  end

  def edit
    @item = Item.find(params[:id])
  end

  def update
    Item.find(params[:id]).update(item_params)
    redirect_to root_path
  end

  def destroy
    Item.find(params[:id]).destroy
    redirect_to root_path
  end

  private

  def item_params
    params.require(:item).permit(:name, :description)
  end
end
