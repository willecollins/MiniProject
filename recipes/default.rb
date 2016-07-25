#
# Cookbook Name:: MiniProject
# Recipe:: default
#
# Copyright (c) 2016 The Authors, All Rights Reserved.


template '/usr/share/nginx/html/index.html' do
  source 'index.html.erb'
end
