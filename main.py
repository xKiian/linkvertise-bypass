import tls_client, uuid, sys, json


class Linkvertise:
    def __init__(self, url: str) -> None:
        self.session = tls_client.Session(
            client_identifier="chrome112", random_tls_extension_order=True
        )  # cloudflare "bypass"

        self.endpoint = "https://publisher.linkvertise.com/graphql"
        self.session.headers = {
            "host": "publisher.linkvertise.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "accept": "application/json",
            "accept-language": "de,en-US;q=0.7,en;q=0.3",
            "accept-encoding": "gzip, deflate, br, zstd",
            "referer": "https://linkvertise.com/",
            "content-type": "application/json",
            "origin": "https://linkvertise.com",
            "connection": "keep-alive",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "priority": "u=0",
        }

        self.url = url
        self.userID = self.url.split("/")[3]
        self.urlName = self.url.split("/")[4]

        self.userIdAndUrl = {"user_id": self.userID, "url": self.urlName}

    def getToken(self) -> str:
        try:
            url = "https://publisher.linkvertise.com/api/v1/account"

            response = self.session.get(url)

            return response.json()["user_token"]
        except json.decoder.JSONDecodeError:
            print("[-] You're probably ratelimited. Try again in 30s-5m")
            exit()

    def getDetailPageContent(self, linkvertiseUT: str) -> str:
        querystring = {"X-Linkvertise-UT": linkvertiseUT}
        payload = {
            "operationName": "getDetailPageContent",
            "variables": {
                "linkIdentificationInput": {"userIdAndUrl": self.userIdAndUrl},
                "additional_data": {
                    "taboola": {
                        "user_id": "{}-tuctd9bb8c6".format(uuid.uuid4()),  # this maybe needs an actual implementation in the future
                        "url": self.url,
                        "test_group": "old",
                    }
                },
            },
            "query": "mutation getDetailPageContent($linkIdentificationInput: PublicLinkIdentificationInput!, $origin: String, $additional_data: CustomAdOfferProviderAdditionalData!) {\n  getDetailPageContent(\n    linkIdentificationInput: $linkIdentificationInput\n    origin: $origin\n    additional_data: $additional_data\n  ) {\n    access_token\n    premium_subscription_active\n    link {\n      id\n      video_url\n      short_link_title\n      recently_edited\n      short_link_title\n      description\n      url\n      seo_faqs {\n        body\n        title\n        __typename\n      }\n      target_host\n      last_edit_at\n      link_images {\n        url\n        __typename\n      }\n      title\n      thumbnail_url\n      view_count\n      is_trending\n      recently_edited\n      seo_faqs {\n        title\n        body\n        __typename\n      }\n      percentage_rating\n      is_premium_only_link\n      publisher {\n        id\n        name\n        subscriber_count\n        __typename\n      }\n      positive_rating\n      negative_rating\n      already_rated_by_user\n      user_rating\n      __typename\n    }\n    linkCustomAdOffers {\n      title\n      call_to_action\n      description\n      countdown\n      completion_token\n      provider\n      provider_additional_payload {\n        taboola {\n          available_event_url\n          visible_event_url\n          __typename\n        }\n        __typename\n      }\n      media {\n        type\n        ... on UrlMediaResource {\n          content_type\n          resource_url\n          __typename\n        }\n        __typename\n      }\n      clickout_action {\n        type\n        ... on CustomAdOfferClickoutUrlAction {\n          type\n          clickout_url\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    link_recommendations {\n      short_link_title\n      target_host\n      id\n      url\n      publisher {\n        id\n        name\n        __typename\n      }\n      last_edit_at\n      link_images {\n        url\n        __typename\n      }\n      title\n      thumbnail_url\n      view_count\n      is_trending\n      recently_edited\n      percentage_rating\n      publisher {\n        name\n        __typename\n      }\n      __typename\n    }\n    target_access_information {\n      remaining_accesses\n      daily_access_limit\n      remaining_waiting_time\n      __typename\n    }\n    __typename\n  }\n}",
        }

        response = self.session.post(self.endpoint, json=payload, params=querystring)

        return response.json()["data"]["getDetailPageContent"]["access_token"]

    def completeDetailPageContent(self, linkvertiseUT: str, token: str) -> str:
        querystring = {"X-Linkvertise-UT": linkvertiseUT}
        payload = {
            "operationName": "completeDetailPageContent",
            "variables": {
                "linkIdentificationInput": {
                    "userIdAndUrl": self.userIdAndUrl
                },
                "completeDetailPageContentInput": {
                    "access_token": token
                },
            },
            "query": "mutation completeDetailPageContent($linkIdentificationInput: PublicLinkIdentificationInput!, $completeDetailPageContentInput: CompleteDetailPageContentInput!) {\n  completeDetailPageContent(\n    linkIdentificationInput: $linkIdentificationInput\n    completeDetailPageContentInput: $completeDetailPageContentInput\n  ) {\n    CUSTOM_AD_STEP\n    TARGET\n    additional_target_access_information {\n      remaining_waiting_time\n      can_not_access\n      should_show_ads\n      has_long_paywall_duration\n      __typename\n    }\n    __typename\n  }\n}",
        }
        
        response = self.session.post(self.endpoint, json=payload, params=querystring)
        
        return response.json()["data"]["completeDetailPageContent"]["TARGET"]

    def getDetailPageTarget(self, linkvertiseUT: str, token: str) -> str:
        querystring = {"X-Linkvertise-UT": linkvertiseUT}
        payload = {
            "operationName": "getDetailPageTarget",
            "variables": {
                "linkIdentificationInput": {
                    "userIdAndUrl": self.userIdAndUrl
                },
                "token": token,
            },
            "query": "mutation getDetailPageTarget($linkIdentificationInput: PublicLinkIdentificationInput!, $token: String!) {\n  getDetailPageTarget(\n    linkIdentificationInput: $linkIdentificationInput\n    token: $token\n  ) {\n    type\n    url\n    paste\n    short_link_title\n    __typename\n  }\n}",
        }

        response = self.session.post(self.endpoint, json=payload, params=querystring)

        data = response.json()["data"]["getDetailPageTarget"]

        if data["type"] == "URL":
            return data["url"]
        
        print(data)
        raise NotImplementedError("This Linkvertise type is not implemented yet")

    def __call__(self) -> str:
        linkvertiseUT = self.getToken()
        token = self.getDetailPageContent(linkvertiseUT)
        token = self.completeDetailPageContent(linkvertiseUT, token)
        result = self.getDetailPageTarget(linkvertiseUT, token)
        
        return result

if __name__ == "__main__":
    if len(sys.argv) == 2:
        res = Linkvertise(url=sys.argv[1])()
    else:
        url = input("[?] Input Linkvertise URL >>> ")
        res = Linkvertise(url=url)()
    
    print("[+]", res)