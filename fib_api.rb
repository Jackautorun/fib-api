require "sinatra"
require "json"

set :bind, "0.0.0.0"
set :port, ENV.fetch("PORT", 4567).to_i

FIB = {0 => 0, 1 => 1}
def fib(n)
  return FIB[n] if FIB.key?(n)
  (2..n).each { |i| FIB[i] = FIB[i-1] + FIB[i-2] }
  FIB[n]
end

get "/fib/:n" do
  n = Integer(params[:n]) rescue halt 400, { error: "n must be integer" }.to_json
  halt 400, { error: "n must be 0..1_000_000" }.to_json unless (0..1_000_000).include?(n)
  content_type :json
  { n: n, value: fib(n) }.to_json
end

