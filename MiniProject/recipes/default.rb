#
# Cookbook Name:: MiniProject
# Recipe:: default
#
# Copyright (c) 2016 The Authors, All Rights Reserved.

package 'httpd'

yum_package 'httpd' do
  action :install
end

template '/var/www/html/index.html' do

  source 'index.html.erb'

end
