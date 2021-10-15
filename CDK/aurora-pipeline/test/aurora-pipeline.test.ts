import { SynthUtils } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as Pipeline from '../lib/aurora-pipeline-stack';

test('Pipeline Stack', () => {
  const app = new cdk.App();
  // WHEN
  const stack = new Pipeline.AuroraPipelineStack(app, 'MyTestStack');
  // THEN
  expect(SynthUtils.toCloudFormation(stack)).toMatchSnapshot();

});
