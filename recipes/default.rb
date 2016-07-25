#
# Cookbook Name:: MiniProject
# Recipe:: default
#
# Copyright (c) 2016 The Authors, All Rights Reserved.


template '/etc/nginx/sites-enabled/index.html' do
  source 'index.html.erb'
end
