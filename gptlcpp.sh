function gptlcpp(){
    head -n 1000 $1 > temp.txt && mv temp.txt $1
    content=$( jq -sR '{"role": "user", "content": .}' $1 )
    response=`curl -s https://aihubmix.com/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: [API-KEY]" \
      -d '{
        "model": "o1-mini",
        "messages": [{"role": "user", "content": "只回答MLIR、NPU、c++相关的内容，详细讲解下面给到的C++代码"}, '"$content"']
      }' | jq ."choices[0].message.content"`;
    echo $response;
}
