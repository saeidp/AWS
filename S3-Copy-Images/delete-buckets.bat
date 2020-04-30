rem aws s3 rm s3://pipe-line-test-2/ss-demo/train --recursive
rem aws s3 rm s3://pipe-line-test-2/ss-demo/train_annotation --recursive
rem aws s3 rm s3://pipe-line-test/ss-demo/validation --recursive
rem aws s3 rm s3://pipe-line-test/ss-demo/validation_annotation --recursive

aws s3 rm s3://pipe-line-test-2/ss-demo-kmeans/train --recursive
aws s3 rm s3://pipe-line-test-2/ss-demo-kmeans/train_annotation --recursive
aws s3 rm s3://pipe-line-test-2/ss-demo-kmeans/validation --recursive
aws s3 rm s3://pipe-line-test-2/ss-demo-kmeans/validation_annotation --recursive