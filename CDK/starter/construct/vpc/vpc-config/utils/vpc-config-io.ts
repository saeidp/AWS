import { readFileSync } from 'fs';
import { isLeft } from 'fp-ts/lib/Either';
import * as t from 'io-ts';
import { PathReporter } from 'io-ts/PathReporter';


const VpcConfigIO = t.type({
    cidrBlock: t.string,
});

export type VpcConfig = t.TypeOf<typeof VpcConfigIO>;

export function validateVpcConfig(rawData: unknown): VpcConfig {
    const decoded = VpcConfigIO.decode(rawData);
    if (isLeft(decoded)) {
        throw new Error(`Invalid configuration file:  ${PathReporter.report(decoded).join('\n')}`);
    }
    return decoded.right;
}

export const readVpcConfig = (vpcConfigPath: string) => {
    try {
        console.log(vpcConfigPath)
        const raw = readFileSync(vpcConfigPath, 'utf8');
        const rawData = JSON.parse(raw);
        return validateVpcConfig(rawData);
    } catch (e) {
        const { message } = e as Error;
        throw new Error(`Unable to load configuration file "${vpcConfigPath}"\n${message}`);
    }
};
