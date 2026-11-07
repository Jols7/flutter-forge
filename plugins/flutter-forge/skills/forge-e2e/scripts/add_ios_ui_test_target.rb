#!/usr/bin/env ruby
# Adds the Patrol RunnerUITests UI-testing target to a Flutter iOS project.
# Usage: ruby add_ios_ui_test_target.rb ios/Runner.xcodeproj <app bundle id>
# Requires the xcodeproj gem (ships with CocoaPods). Then add to ios/Podfile, inside target 'Runner':
#   target 'RunnerUITests' do
#     inherit! :complete
#   end
# and create ios/RunnerUITests/RunnerUITests.m with PATROL_INTEGRATION_TEST_IOS_RUNNER(RunnerUITests).
require 'xcodeproj'
proj_path = ARGV[0]
bundle_id = ARGV[1]
project = Xcodeproj::Project.open(proj_path)
abort('RunnerUITests already exists') if project.targets.any? { |t| t.name == 'RunnerUITests' }
runner = project.targets.find { |t| t.name == 'Runner' }
deployment = runner.build_configurations.first.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] ||
             project.build_configurations.first.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] || '15.0'
deployment = '15.0' if Gem::Version.new(deployment) < Gem::Version.new('15.0')   # Xcode 27 minimum

target = project.new_target(:ui_test_bundle, 'RunnerUITests', :ios, deployment)
target.add_dependency(runner)

group = project.main_group.find_subpath('RunnerUITests', true)
group.set_source_tree('<group>')
group.set_path('RunnerUITests')
file = group.new_reference('RunnerUITests.m')
target.add_file_references([file])

target.build_configurations.each do |config|
  runner_config = runner.build_configurations.find { |c| c.name == config.name }
  config.base_configuration_reference = runner_config&.base_configuration_reference
  s = config.build_settings
  s['PRODUCT_BUNDLE_IDENTIFIER'] = "#{bundle_id}.RunnerUITests"
  s['PRODUCT_NAME'] = '$(TARGET_NAME)'
  s['TEST_TARGET_NAME'] = 'Runner'
  s['EXCLUDED_ARCHS[sdk=iphonesimulator*]'] = 'x86_64'
  s['GENERATE_INFOPLIST_FILE'] = 'YES'
  s['IPHONEOS_DEPLOYMENT_TARGET'] = deployment
  s['ENABLE_USER_SCRIPT_SANDBOXING'] = 'NO'
  s['CLANG_ENABLE_MODULES'] = 'YES'
  s['TARGETED_DEVICE_FAMILY'] = '1,2'
  s['CODE_SIGN_STYLE'] = 'Automatic'
  s.delete('SWIFT_VERSION')
end

build = target.new_shell_script_build_phase('xcode_backend build')
build.shell_script = "/bin/sh \"$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh\" build\n"
target.build_phases.delete(build)
target.build_phases.insert(0, build)
embed = target.new_shell_script_build_phase('xcode_backend embed_and_thin')
embed.shell_script = "/bin/sh \"$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh\" embed_and_thin\n"
project.save

scheme_path = File.join(proj_path, 'xcshareddata', 'xcschemes', 'Runner.xcscheme')
scheme = Xcodeproj::XCScheme.new(scheme_path)
scheme.add_test_target(target)
scheme.save!
puts "added RunnerUITests (iOS #{deployment})"
